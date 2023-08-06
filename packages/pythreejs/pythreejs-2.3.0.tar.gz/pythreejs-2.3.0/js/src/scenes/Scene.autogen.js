//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var Promise = require('bluebird');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');
var serializers = require('../_base/serializers');

var Object3DModel = require('../core/Object3D.js').Object3DModel;

var FogModel = require('./Fog.autogen.js').FogModel;
var FogExp2Model = require('./FogExp2.autogen.js').FogExp2Model;
var MaterialModel = require('../materials/Material.js').MaterialModel;

var SceneModel = Object3DModel.extend({

    defaults: function() {
        return _.extend(Object3DModel.prototype.defaults.call(this), {

            fog: null,
            overrideMaterial: null,
            autoUpdate: true,
            background: "#ffffff",
            type: "Scene",

        });
    },

    constructThreeObject: function() {

        var result = new THREE.Scene();
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        Object3DModel.prototype.createPropertiesArrays.call(this);
        this.three_properties.push('fog');
        this.three_properties.push('overrideMaterial');

        this.props_created_by_three['type'] = true;
        this.props_created_by_three['matrixWorldNeedsUpdate'] = true;

        this.property_converters['fog'] = 'convertThreeType';
        this.property_converters['overrideMaterial'] = 'convertThreeType';
        this.property_converters['autoUpdate'] = 'convertBool';
        this.property_converters['background'] = 'convertColor';
        this.property_converters['type'] = null;


    },

}, {

    model_name: 'SceneModel',

    serializers: _.extend({
        fog: { deserialize: serializers.unpackThreeModel },
        overrideMaterial: { deserialize: serializers.unpackThreeModel },
    },  Object3DModel.serializers),
});

module.exports = {
    SceneModel: SceneModel,
};
