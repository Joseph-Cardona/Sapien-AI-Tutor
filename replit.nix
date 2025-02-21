{pkgs}: {
  deps = [
    pkgs.espeak-ng
    pkgs.tesseract
    pkgs.libGLU
    pkgs.libGL
    pkgs.rustc
    pkgs.libiconv
    pkgs.cargo
  ];
}
