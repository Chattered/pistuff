{ pkgs ? (import <nixpkgs> {}).pkgs
}:
let
  myemacs =
    with pkgs.emacsPackages; pkgs.emacsWithPackages
      [ pkgs.emacsPackagesNg.elpy magit emacsw3m org ];
in with pkgs; stdenv.mkDerivation {
  name = "pistuff";
  buildInputs = [ myemacs python3 pythonPackages.pygments texLiveFull which ];
  shellHook = ''
    emacs-tcp maze .emacs
  '';
}
#TODO: Dependency on which should be made runtime.
