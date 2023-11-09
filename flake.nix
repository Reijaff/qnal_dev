{
  description = "Python DevShell";

  inputs = {

    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    flake-utils.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};

        blender = pkgs.blender.withPackages (ps: with ps; [ 
          bpycv 
          tqdm 
          ]);
      in {
        devShells = {
          default = (pkgs.buildFHSEnv rec {
            name = "qnal-zone";
            profile = (''
              export PATH=$PATH:${blender.outPath}/bin
            ''
            );
            targetPkgs = pkgs:
              with pkgs; [
                blender

                (python3.withPackages (p:
                  with p; [
                    flask
                    numpy
                    scipy
                    ipython

                    requests
                    filelock
                    tqdm
                    pyyaml

                    # fake-bpy-module-latest

                    (buildPythonPackage rec {
                      pname = "fake-bpy-module-latest";
                      version = "20231106";
                      src = fetchPypi {
                        inherit pname version;
                        sha256 =
                          "sha256-rq5XfPI1qSa+viHTqt2G+f/QiwAReay9t/StG9GTguE=";
                      };
                      doCheck = false;
                    })

                    (buildPythonPackage rec {
                      pname = "huggingface_hub";
                      version = "0.18.0";
                      src = fetchPypi {
                        inherit pname version;
                        sha256 =
                          "sha256-EO2hK5wc+oALS3wJazrOiENzTD8o1p0cJDdD+316LoE=";
                      };
                      doCheck = false;
                    })

                    (buildPythonPackage rec {
                      pname = "balacoon-tts";
                      version = "0.1.3";
                      src = fetchurl {
                        url =
                          "https://pypi.fury.io/balacoon/-/ver_KyTm0/balacoon_tts-0.1.3-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.manylinux_2_24_x86_64.whl";
                        sha256 =
                          "sha256-u0jhna7QHlj7sjdeNmDi08WNr++d+wQb+wFFYr0bm9s=";
                      };
                      format = "wheel";
                      doCheck = false;
                      buildInputs = [ ];
                      checkInputs = [ ];
                      nativeBuildInputs = [ ];
                      propagatedBuildInputs = [ ];
                    }

                    )

                    # ansible 
                    # jmespath 
                  ]))

                (vscode-with-extensions.override {
                  vscode = vscodium;
                  vscodeExtensions = with vscode-extensions;
                    [
                      vscodevim.vim
                      ms-python.python
                      # ms-python.autopep8
                      # JacquesLucke.blender-development
                      # ms-azuretools.vscode-docker
                      # ms-vscode-remote.remote-ssh
                    ] ++ pkgs.vscode-utils.extensionsFromVscodeMarketplace [{
                      name = "blender-development";
                      publisher = "JacquesLucke";
                      version = "0.0.18";
                      sha256 =
                        "sha256-C/ytfJnjTHwkwHXEYah4FGKNl1IKWd2wCGFSPjlo13s=";
                    }
                    # {
                    # name = "autopep8";
                    # publisher = "ms-python";
                    # version = "2023.9.13101009";
                    # sha256 = "sha256-4wzfkKha5olcDb03LsaIh6RKAJO7OLtpArogP04wRlw=";
                    # }
                    ];
                })

                (texlive.combine {
                  inherit (pkgs.texlive)
                    scheme-basic standalone preview # definately needed
                    dvisvgm dvipng # for preview and export as html
                    wrapfig amsmath ulem hyperref capt-of; # probably needed
                  #(setq org-latex-compiler "lualatex")
                  #(setq org-preview-latex-default-process 'dvisvgm)
                })

              ];
            runScript = ''
              bash script.sh
            '';
          }).env;
        };
      });
}
