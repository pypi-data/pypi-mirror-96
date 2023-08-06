//
// This file auto-generated with generate-wrappers.js
//
// Load all three.js python wrappers
var loadedModules = [
    require('./CompressedTexture.autogen.js'),
    require('./CubeTexture.autogen.js'),
    require('./DataTexture.autogen.js'),
    require('./DataTexture.js'),
    require('./DataTexture3D.autogen.js'),
    require('./DataTexture3D.js'),
    require('./DepthTexture.autogen.js'),
    require('./DepthTexture.js'),
    require('./ImageTexture.autogen.js'),
    require('./ImageTexture.js'),
    require('./TextTexture.autogen.js'),
    require('./TextTexture.js'),
    require('./Texture.autogen.js'),
    require('./VideoTexture.autogen.js'),
];

for (var i in loadedModules) {
    if (loadedModules.hasOwnProperty(i)) {
        var loadedModule = loadedModules[i];
        for (var target_name in loadedModule) {
            if (loadedModule.hasOwnProperty(target_name)) {
                module.exports[target_name] = loadedModule[target_name];
            }
        }
    }
}

