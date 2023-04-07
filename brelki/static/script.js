import { GLTFLoader } from 'C:/Program Files/nodejs/node_modules/three/examples/jsm/loaders';
import model from 'C:/projects/brelki/brelki/static/Audi R8.fbx';
let loader = new GLTFLoader();
loader.load(model, function (geometry) {
    const scene = gltf.scene;

    scene.add( gltf.scene );
}, undefined, function (err) {
  console.error(err);
});