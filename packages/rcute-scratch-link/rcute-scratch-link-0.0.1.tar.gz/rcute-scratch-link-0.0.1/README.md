# rcute-scratch-link

scratch link for rcute extensions, it can run alongside the offical scratch link.

## install
install [rcute-cozmars](https://github.com/r-cute/rcute-cozmars) and [rcute-ai](https://github.com/r-cute/rcute-ai), then
`python3 -m pip install rcute-scratch-link`

## run
`python3 -m rcute_scratch_link -v`

## scratch3 with rcute extensions

### install
```
git clone https://github.com/r-cute/rcute-scratch-gui.git --depth=1
git clone https://github.com/r-cute/rcute-scratch-vm.git --depth=1
git clone https://github.com/r-cute/rcute-scratch-blocks.git --depth=1

cd rcute-scratch-blocks
yarn install
yarn link

cd ../rcute-scratch-vm
yarn link scratch-blocks
yarn install
yarn link

cd ../rcute-scratch-gui
yarn link scratch-blocks
yarn link scratch-vm
yarn install
```

### start scratch3
```
cd rcute-scratch-gui
yarn start
```