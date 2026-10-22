#define FETCH_CODENAME "test"
#define FETCH_ARCH "test"
#define FETCH_OS "test"
#define main fetch_program_main
#include "../fetch.c"
#undef main

static int failures;
#define CHECK(test) do { \
  if (!(test)) { fprintf(stderr, "FAIL line %d: %s\n", __LINE__, #test); failures++; } \
} while (0)

static void test_info_bounds(void) {
  fetch_line_count = 0;
  for (int i = 0; i < F_COUNT; i++) field_line[i] = -1;
  current_field = -1;
  add_line("title");
  add_line("-----");

  char long_value[MAX_LINE_LEN];
  memset(long_value, 'x', sizeof(long_value) - 1);
  long_value[sizeof(long_value) - 1] = '\0';
  for (int i = 0; i < MAX_FETCH_LINES - 2; i++) {
    current_field = i == 0 ? F_UPTIME : F_MEMORY;
    add_info("Long field", "%s", long_value);
  }
  current_field = F_GPU;
  add_info("Dropped", "value");
  CHECK(fetch_line_count == MAX_FETCH_LINES);
  CHECK(field_line[F_GPU] == -1);

  box_wrap_lines();
  CHECK(fetch_line_count == MAX_FETCH_LINES);
  CHECK(field_line[F_UPTIME] == 3);
  CHECK(field_line[F_MEMORY] == -1);
  CHECK(box_width > 0 && box_width <= (MAX_LINE_LEN - 16) / 3);
  CHECK(strstr(fetch_lines[2], "\xe2\x95\xad") == fetch_lines[2]);
  CHECK(strstr(fetch_lines[MAX_FETCH_LINES - 1], "\xe2\x95\xb0") ==
        fetch_lines[MAX_FETCH_LINES - 1]);
  for (int i = 2; i < fetch_line_count; i++) {
    CHECK(memchr(fetch_lines[i], '\0', MAX_LINE_LEN) != NULL);
    CHECK(visible_width(fetch_lines[i]) == box_width + 4);
  }

  is_refresh_pass = 1;
  current_field = F_UPTIME;
  add_info("Uptime", "refreshed");
  CHECK(fetch_line_count == MAX_FETCH_LINES);
  CHECK(strstr(fetch_lines[field_line[F_UPTIME]], "refreshed") != NULL);
  CHECK(visible_width(fetch_lines[field_line[F_UPTIME]]) == box_width + 4);
  is_refresh_pass = 0;
  box_width = 0;
}

static void test_minimal_logos(void) {
  for (int shape = 0; shape < 3; shape++) {
    logo_rows = shape == 2 ? 3 : 1;
    for (int r = 0; r < logo_rows; r++)
      strcpy(logo_data[r], shape == 1 ? "@@@" : "@");
    process_logo();
    POINT_COUNT = 0;
    config_depth = 1.0f;
    depth_user_set = 1;
    build_points();
    CHECK(POINT_COUNT > 0);
    for (int i = 0; i < POINT_COUNT; i++)
      CHECK(isfinite(PX[i]) && isfinite(PY[i]) && isfinite(PZ[i]) &&
            isfinite(NX[i]) && isfinite(NY[i]) && isfinite(NZ[i]));
  }
}

static void test_distro_brand_colors(void) {
  // Known distros resolve to their brand color.
  const distro_brand *arch = lookup_brand("arch");
  CHECK(arch != NULL);
  CHECK(arch && arch->r == 0 && arch->g == 170 && arch->b == 238);

  const distro_brand *bazzite = lookup_brand("bazzite");
  CHECK(bazzite && bazzite->r == 138 && bazzite->g == 43 && bazzite->b == 226);

  const distro_brand *ubuntu = lookup_brand("ubuntu");
  CHECK(ubuntu && ubuntu->r == 233 && ubuntu->g == 84 && ubuntu->b == 32);

  const distro_brand *mint = lookup_brand("linuxmint");
  CHECK(mint && mint->r == 134 && mint->g == 190 && mint->b == 67);

  const distro_brand *redhat = lookup_brand("redhat");
  CHECK(redhat && redhat->r == 238 && redhat->g == 0 && redhat->b == 0);

  // Aliases and suffixed variants resolve to the same entry.
  CHECK(lookup_brand("mint") == mint);
  CHECK(lookup_brand("linuxmint") == mint);
  CHECK(lookup_brand("fedora-asahi-remix") == lookup_brand("asahi"));
  CHECK(lookup_brand("opensuse-leap") == lookup_brand("opensuse"));

  // Unknown distros match nothing.
  CHECK(lookup_brand("notadistro") == NULL);
  CHECK(lookup_brand("") == NULL);
  CHECK(lookup_brand(NULL) == NULL);
}

// The logo's main color is the one most of its cells wear, white aside.
static void test_logo_main_color(void) {
  logo_has_ansi = 1;
  logo_rows = 2;
  logo_cell_counts[0] = 4;
  logo_cell_counts[1] = 4;
  for (int c = 0; c < 4; c++) {
    logo_cell_color[0][c] = 36;
    logo_cell_color[1][c] = 37;
  }
  CHECK(logo_main_color() == 36);

  // A logo painted mostly white still reports a real color when it has one.
  logo_cell_color[0][0] = 32;
  logo_cell_color[0][1] = 32;
  CHECK(logo_main_color() == 32);

  // White only: the logo is a white silhouette.
  for (int c = 0; c < 4; c++)
    logo_cell_color[0][c] = 37;
  CHECK(logo_main_color() == 37);

  // A logo without any colors of its own has no main color.
  logo_has_ansi = 0;
  CHECK(logo_main_color() == 0);
  logo_has_ansi = 1;
}

// The labels take the color the logo is drawn in.
static void test_labels_follow_the_logo(void) {
  // A logo drawn in cyan gives cyan labels.
  logo_has_ansi = 1;
  logo_rows = 1;
  logo_cell_counts[0] = 3;
  for (int c = 0; c < 3; c++)
    logo_cell_color[0][c] = 36;
  label_color_set = 0;
  set_distro_colors("arch");
  CHECK(strcmp(label_color, "36") == 0);

  // A logo drawn in green with white highlights gives green labels.
  logo_rows = 2;
  logo_cell_counts[0] = 3;
  logo_cell_counts[1] = 3;
  for (int c = 0; c < 3; c++) {
    logo_cell_color[0][c] = 32;
    logo_cell_color[1][c] = 37;
  }
  set_distro_colors("linuxmint");
  CHECK(strcmp(label_color, "32") == 0);

  // A logo without colors of its own falls back to the brand color, and the
  // logo is painted in it too.
  logo_has_ansi = 0;
  label_color_set = 0;
  config_truecolor = 1;
  set_distro_colors("bazzite");
  CHECK(strcmp(label_color, "38;2;138;43;226") == 0);
  CHECK(strstr(color_outer, "38;2;138;43;226") != NULL);

  // An explicit choice is never overridden.
  label_color_set = 1;
  strcpy(label_color, "32");
  set_distro_colors("bazzite");
  CHECK(strcmp(label_color, "32") == 0);

  label_color_set = 0;
  config_truecolor = -1;
  strcpy(label_color, "35");
}

static void test_label_color(void) {
  // 24-bit color uses the exact brand RGB.
  label_color_set = 0;
  config_truecolor = 1;
  set_label_rgb(23, 147, 209, 36);
  CHECK(strcmp(label_color, "38;2;23;147;209") == 0);

  // Without it, the nearest 16-color code is used.
  config_truecolor = 0;
  set_label_rgb(23, 147, 209, 36);
  CHECK(strcmp(label_color, "36") == 0);

  // An explicit choice is never overridden.
  label_color_set = 1;
  strcpy(label_color, "32");
  config_truecolor = 1;
  set_label_rgb(233, 84, 32, 31);
  CHECK(strcmp(label_color, "32") == 0);

  // The same applies to the os-release fallback.
  strcpy(label_color, "32");
  set_label_from_os_release("/etc/os-release");
  CHECK(strcmp(label_color, "32") == 0);

  label_color_set = 0;
  config_truecolor = -1;
  strcpy(label_color, "35");
}

static void test_os_release_color(void) {
  const char *path = "tests/os-release.tmp";
  FILE *fp = fopen(path, "w");
  CHECK(fp != NULL);
  if (!fp)
    return;
  fprintf(fp, "NAME=\"Test Linux\"\nID=testlinux\n");
  fprintf(fp, "ANSI_COLOR=\"38;2;11;22;33\"\n");
  fclose(fp);

  label_color_set = 0;
  strcpy(label_color, "35");
  set_label_from_os_release(path);
  CHECK(strcmp(label_color, "38;2;11;22;33") == 0);

  // A 256-color hint is passed through as-is.
  fp = fopen(path, "w");
  fprintf(fp, "ANSI_COLOR=\"0;135\"\n");
  fclose(fp);
  strcpy(label_color, "35");
  set_label_from_os_release(path);
  CHECK(strcmp(label_color, "38;5;135") == 0);

  // A plain 16-color hint is used directly.
  fp = fopen(path, "w");
  fprintf(fp, "ANSI_COLOR=\"1;34\"\n");
  fclose(fp);
  strcpy(label_color, "35");
  set_label_from_os_release(path);
  CHECK(strcmp(label_color, "34") == 0);

  // No hint at all leaves the color alone.
  fp = fopen(path, "w");
  fprintf(fp, "ID=testlinux\n");
  fclose(fp);
  strcpy(label_color, "35");
  set_label_from_os_release(path);
  CHECK(strcmp(label_color, "35") == 0);

  remove(path);
}

int main(void) {
  test_info_bounds();
  test_minimal_logos();
  test_distro_brand_colors();
  test_logo_main_color();
  test_labels_follow_the_logo();
  test_label_color();
  test_os_release_color();
  printf("Shared unit tests: %s\n", failures ? "FAILED" : "passed");
  return failures ? 1 : 0;
}
