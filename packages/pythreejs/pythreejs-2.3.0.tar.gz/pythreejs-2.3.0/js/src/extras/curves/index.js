//
// This file auto-generated with generate-wrappers.js
//
// Load all three.js python wrappers
var loadedModules = [
    require('./ArcCurve.autogen.js'),
    require('./CatmullRomCurve3.autogen.js'),
    require('./CubicBezierCurve.autogen.js'),
    require('./CubicBezierCurve3.autogen.js'),
    require('./EllipseCurve.autogen.js'),
    require('./LineCurve.autogen.js'),
    require('./LineCurve3.autogen.js'),
    require('./QuadraticBezierCurve.autogen.js'),
    require('./QuadraticBezierCurve3.autogen.js'),
    require('./SplineCurve.autogen.js'),
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

