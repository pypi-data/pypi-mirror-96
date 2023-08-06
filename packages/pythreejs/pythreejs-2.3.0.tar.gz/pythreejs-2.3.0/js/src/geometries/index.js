//
// This file auto-generated with generate-wrappers.js
//
// Load all three.js python wrappers
var loadedModules = [
    require('./BoxBufferGeometry.autogen.js'),
    require('./BoxGeometry.autogen.js'),
    require('./BoxLineGeometry.autogen.js'),
    require('./CircleBufferGeometry.autogen.js'),
    require('./CircleGeometry.autogen.js'),
    require('./ConeGeometry.autogen.js'),
    require('./CylinderBufferGeometry.autogen.js'),
    require('./CylinderGeometry.autogen.js'),
    require('./DodecahedronGeometry.autogen.js'),
    require('./EdgesGeometry.autogen.js'),
    require('./EdgesGeometry.js'),
    require('./ExtrudeGeometry.autogen.js'),
    require('./IcosahedronGeometry.autogen.js'),
    require('./LatheBufferGeometry.autogen.js'),
    require('./LatheGeometry.autogen.js'),
    require('./LineGeometry.autogen.js'),
    require('./LineGeometry.js'),
    require('./LineSegmentsGeometry.autogen.js'),
    require('./LineSegmentsGeometry.js'),
    require('./OctahedronGeometry.autogen.js'),
    require('./ParametricGeometry.autogen.js'),
    require('./PlaneBufferGeometry.autogen.js'),
    require('./PlaneGeometry.autogen.js'),
    require('./PolyhedronGeometry.autogen.js'),
    require('./RingBufferGeometry.autogen.js'),
    require('./RingGeometry.autogen.js'),
    require('./ShapeGeometry.autogen.js'),
    require('./SphereBufferGeometry.autogen.js'),
    require('./SphereGeometry.autogen.js'),
    require('./TetrahedronGeometry.autogen.js'),
    require('./TextGeometry.autogen.js'),
    require('./TorusBufferGeometry.autogen.js'),
    require('./TorusGeometry.autogen.js'),
    require('./TorusKnotBufferGeometry.autogen.js'),
    require('./TorusKnotGeometry.autogen.js'),
    require('./TubeGeometry.autogen.js'),
    require('./WireframeGeometry.autogen.js'),
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

