//
// This file auto-generated with generate-wrappers.js
//
// Load all three.js python wrappers
var loadedModules = [
    require('./LineBasicMaterial.autogen.js'),
    require('./LineDashedMaterial.autogen.js'),
    require('./LineMaterial.autogen.js'),
    require('./LineMaterial.js'),
    require('./Material.autogen.js'),
    require('./Material.js'),
    require('./MeshBasicMaterial.autogen.js'),
    require('./MeshDepthMaterial.autogen.js'),
    require('./MeshLambertMaterial.autogen.js'),
    require('./MeshMatcapMaterial.autogen.js'),
    require('./MeshNormalMaterial.autogen.js'),
    require('./MeshPhongMaterial.autogen.js'),
    require('./MeshPhysicalMaterial.autogen.js'),
    require('./MeshStandardMaterial.autogen.js'),
    require('./MeshToonMaterial.autogen.js'),
    require('./PointsMaterial.autogen.js'),
    require('./RawShaderMaterial.autogen.js'),
    require('./ShaderMaterial.autogen.js'),
    require('./ShadowMaterial.autogen.js'),
    require('./SpriteMaterial.autogen.js'),
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

