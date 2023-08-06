//
// This file auto-generated with generate-wrappers.js
//
// Load all three.js python wrappers
var loadedModules = [
    require('./Curve.autogen.js'),
    require('./CurvePath.autogen.js'),
    require('./Font.autogen.js'),
    require('./Path.autogen.js'),
    require('./Shape.autogen.js'),
    require('./ShapePath.autogen.js'),
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

