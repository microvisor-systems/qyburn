{
  pkgs,
  lib,
  config,
  inputs,
  ...
}:

let
  CONSTANTS = rec {
    IBM = {
      DOMAIN = "https://ibm.com/ca-en";
    };
  };

  PORTS = {
    DOCS = "5173";
  };

  URLS = rec {
    SCHEME = "http";
    HOST = "127.0.0.1";
    LOCALHOST = "${SCHEME}://${HOST}:";
  };

  # FLAGS = {
  #   DEVELOPMENT = true;
  # };
in
{
  name = "🧮 Microvisor 🧮";

  infoSections = {
    name = [ "Mumtahin Farabi" ];
  };

  imports = [
    ./languages
    ./scripts.nix
    ./packages.nix
    ./processes.nix
  ];

  env = {
    GREET = "Qyburn";
    # IBM_QUANTUM_CRN = "";
    # IBM_QUANTUM_API_TOKEN = "";
  };

  # services.postgres.enable = true;

  scripts = {
    hello.exec = ''
      echo hello from $GREET
    '';
  };

  # tasks = {
  #   "myproj:setup".exec = "mytool build";
  #   "devenv:enterShell".after = [ "myproj:setup" ];
  # };

  enterTest = ''
    echo "Running tests"
    git --version | grep --color=auto "${pkgs.git.version}"
  '';

  enterShell = ''
    devenv info
  '';
}
