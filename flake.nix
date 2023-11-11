{
  inputs = {

    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    # flake-utils.url = "github:numtide/flake-utils";
    # flake-utils.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = { self, nixpkgs, flake-utils }:

    flake-utils.lib.eachDefaultSystem (system:
      let
        # nixpkgs.config.allowUnfree = true;
        # nixpkgs.config.allowUnfree = true;
        # pkgs = nixpkgs.legacyPackages.${system};
        pkgs = import nixpkgs {
            config = {
              # CUDA and other "friends" contain unfree licenses. To install them, you need this line:
              allowUnfree = true;
            };
            inherit system;
        };


        v1 = {
          name = "MACHIN3tools";
          src = builtins.fetchGit {
            url = "https://github.com/machin3io/MACHIN3tools";
            rev = "db0590bc624407d07d5c0f08ced2872c04c49d4c";
          };
        };

        initScript = pkgs.writeScript "run.sh" ''
          # echo Reinstalling blender plugins ...

          echo Installing ${v1.name}
          rm -rf $XDG_CONFIG_HOME/blender/3.6/scripts/addons/${v1.name}/
          mkdir -p $XDG_CONFIG_HOME/blender/3.6/scripts/addons/${v1.name}
          cp -r ${v1.src}/* $XDG_CONFIG_HOME/blender/3.6/scripts/addons/${v1.name}
          chmod 755 -R $XDG_CONFIG_HOME/blender/3.6/scripts/addons/${v1.name}


          echo Starting tts server ... 
          python tts_server.py &

          bash

          trap '
            echo "Exiting the shell ... "
            trap 'rm -rf config/Code/Workspaces/*' EXIT
            pkill -f tts_server.py
          ' EXIT
        '';


        blender = nixpkgs.legacyPackages.${system}.blender.withPackages (ps:
          with ps; [
            bpycv
            tqdm
            debugpy
            requests
            flask

          ]);
        
      in {
        devShells = {
          default = (pkgs.buildFHSEnv rec {
            name = "qnal-zone";
            profile = (''
              export PATH=$PATH:${blender.outPath}/bin
              export XDG_CONFIG_HOME=$PWD/config
            '');

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
                    })


                    # ansible 
                    # jmespath 
                  ]))

                (vscode-with-extensions.override {
                  # vscode = vscodium;
                  vscodeExtensions = with vscode-extensions;
                    [
                      vscodevim.vim
                      ms-python.python
                      ms-vscode.cpptools
                    ] ++ pkgs.vscode-utils.extensionsFromVscodeMarketplace [{
                      name = "blender-development";
                      publisher = "JacquesLucke";
                      version = "0.0.18";
                      sha256 =
                        "sha256-C/ytfJnjTHwkwHXEYah4FGKNl1IKWd2wCGFSPjlo13s=";

                    }
                    
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
            runScript = initScript;
          }).env;
        };
      });
}
