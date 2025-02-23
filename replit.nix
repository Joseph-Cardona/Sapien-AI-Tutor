{pkgs}: {
  deps = [
    pkgs.tesseract
    pkgs.espeak-ng
    pkgs.libGLU
    pkgs.libGL
    pkgs.rustc
    pkgs.libiconv
    pkgs.cargo
  ];
}
