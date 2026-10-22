{
  lib,
  stdenv,
  makeWrapper,
  fastfetch,
  # linux-only
  pciutils,
}:

stdenv.mkDerivation (finalAttrs: {
  pname = "3dfetch";
  version = lib.fileContents ../VERSION;
  __structuredAttrs = true;
  strictDeps = true;

  src = lib.cleanSource ../.;

  makeFlags = [ "PREFIX=${placeholder "out"}" ];
  nativeBuildInputs = [ makeWrapper ];
  postInstall = ''
    for prog in fetch 3dfetch; do
      wrapProgram $out/bin/$prog \
      --prefix PATH : ${
        lib.makeBinPath ([ fastfetch ] ++ lib.optionals stdenv.hostPlatform.isLinux [ pciutils ])
      }
    done
  '';

  meta = {
    description = "Animated 3D fetch tool that renders your distro logo as a spinning bas-relief";
    homepage = "https://github.com/Rutytoi220/3dfetch";
    changelog = "https://github.com/Rutytoi220/3dfetch/releases/tag/v${finalAttrs.version}";
    license = lib.licenses.isc;
    mainProgram = "3dfetch";
    platforms = lib.platforms.unix;
  };
})
