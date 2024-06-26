{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
  };

  outputs = {
    self,
    nixpkgs,
    flake-utils,
  }:
    flake-utils.lib.eachDefaultSystem (system: let
      pkgs = import nixpkgs {
        config = {
          allowUnfree = true;
        };
        inherit system;
      };

      bforartists = builtins.fetchTarball {
        url = "https://www.bforartists.de/data/binaries/Bforartists-4.0.2-Linux.tar.xz";
        sha256 = "0f2qcwpwfkx1jgh4647q7l3pz140axhnkwbnfwj12jqyfrw3dci6";
      };

      initScript = pkgs.writeScript "run.sh" ''
        # echo Reinstalling blender plugins ...

        ${builtins.foldl' (a: b: a + b.ri) ""
          (import ./modules/blender_plugins.nix).plugins}

        echo Starting tts server ...
        python tts_server.py &

        bash

        trap '
          echo "Exiting the shell ... "
          rm -r config/Code/Workspaces/*
          pkill -f tts_server.py
        ' EXIT
      '';
      # blender = nixpkgs.legacyPackages.${system}.blender.withPackages (ps:
      # with ps; [
      # # bpycv
      # tqdm
      # debugpy
      # requests
      # flask
      # ]);

      bforartists_python = pkgs.python310.withPackages (p:
        with p; [
          numpy
          debugpy
          flask
          requests
          tqdm
        ]);

      fhs = pkgs.buildFHSEnv rec {
        multiPkgs = pkgs.steam.args.multiPkgs; # for bforartists , universal
        name = "qnal-zone";
        # export PATH=$PATH:${blender.outPath}/bin
        profile = ''
          export XDG_CONFIG_HOME=$PWD/config
          export PATH=$PATH:${bforartists}/
          export BLENDER_SYSTEM_PYTHON=${bforartists_python}
        '';

        targetPkgs = pkgs:
          with pkgs; [
            ffmpeg
            # blender
            piper-tts

            libdecor # for bforartists

            (python3.withPackages (p:
              with p; [
                flask
                numpy
                scipy

                # ipython
                debugpy

                requests
                filelock
                tqdm
                pyyaml
                pytaglib
                torchaudio
                omegaconf
                rich
                soundfile
                piper-phonemize
                tabulate
                # piper-tts
                # deepspeed

                (buildPythonPackage rec {
                  pname = "deepspeed";
                  version = "";
                  src = fetchGit {
                    url = "https://github.com/microsoft/DeepSpeed";
                    rev = "4d866bd55a6b2b924987603b599c1f8f35911c4b";
                  };
                  doCheck = false;
                })
                py-cpuinfo
                psutil
                hjson
                pydantic
                librosa
                pandas
                matplotlib

                # resemble-enhance
                (buildPythonPackage rec {
                  pname = "resemble-enhance";
                  version = "0.0.1";
                  src = fetchGit {
                    url = "https://github.com/resemble-ai/resemble-enhance";
                    rev = "b4bd8d693a8353617bba7d0cd0fb2e8c4e586527";
                  };
                  doCheck = false;
                })

                dtw-python
                openai-whisper
                (buildPythonPackage rec {
                  pname = "whisper-timestamped";
                  version = "";
                  src = fetchGit {
                    url = "https://github.com/linto-ai/whisper-timestamped";
                    rev = "a0b86f283336256156f552842d5a99c5101a157a";
                  };
                  doCheck = false;
                })

                #
                huggingface-hub

                (buildPythonPackage rec {
                  pname = "fake-bpy-module-latest";
                  version = "20231106";
                  src = fetchPypi {
                    inherit pname version;
                    sha256 = "sha256-rq5XfPI1qSa+viHTqt2G+f/QiwAReay9t/StG9GTguE=";
                  };
                  doCheck = false;
                })

                (buildPythonPackage rec {
                  pname = "balacoon-tts";
                  version = "0.1.3";
                  src = fetchurl {
                    url = "https://pypi.fury.io/balacoon/-/ver_KyTm0/balacoon_tts-0.1.3-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.manylinux_2_24_x86_64.whl";
                    sha256 = "sha256-u0jhna7QHlj7sjdeNmDi08WNr++d+wQb+wFFYr0bm9s=";
                  };
                  format = "wheel";
                  doCheck = false;
                  buildInputs = [];
                  checkInputs = [];
                  nativeBuildInputs = [];
                  propagatedBuildInputs = [];
                })

                # ansible
                # jmespath
              ]))
            bforartists_python

            (vscode-with-extensions.override {
              # vscode = vscodium;
              vscodeExtensions = with vscode-extensions;
                [vscodevim.vim ms-python.python ms-vscode.cpptools]
                ++ pkgs.vscode-utils.extensionsFromVscodeMarketplace [
                  {
                    name = "blender-development";
                    publisher = "JacquesLucke";
                    version = "0.0.18";
                    sha256 = "sha256-C/ytfJnjTHwkwHXEYah4FGKNl1IKWd2wCGFSPjlo13s=";
                  }
                ];
            })

            (texlive.combine {
              inherit
                (pkgs.texlive)
                scheme-basic
                standalone
                preview # definately needed
                dvisvgm
                dvipng # for preview and export as html
                wrapfig
                amsmath
                ulem
                hyperref
                capt-of
                ; # probably needed
              #(setq org-latex-compiler "lualatex")
              #(setq org-preview-latex-default-process 'dvisvgm)
            })
          ];
        runScript = initScript;
      };
    in {
      devShells = {
        default = fhs.env;
      };
    });
}
