//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var Promise = require('bluebird');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');
var serializers = require('../_base/serializers');

var MaterialModel = require('./Material.js').MaterialModel;

var TextureModel = require('../textures/Texture.autogen.js').TextureModel;

var SpriteMaterialModel = MaterialModel.extend({

    defaults: function() {
        return _.extend(MaterialModel.prototype.defaults.call(this), {

            color: "#ffffff",
            fog: false,
            lights: false,
            map: null,
            rotation: 0,
            sizeAttenuation: true,
            type: "SpriteMaterial",

        });
    },

    constructThreeObject: function() {

        var result = new THREE.SpriteMaterial(
            {
                color: this.convertColorModelToThree(this.get('color'), 'color'),
                fog: this.convertBoolModelToThree(this.get('fog'), 'fog'),
                lights: this.convertBoolModelToThree(this.get('lights'), 'lights'),
                map: this.convertThreeTypeModelToThree(this.get('map'), 'map'),
                rotation: this.convertFloatModelToThree(this.get('rotation'), 'rotation'),
                sizeAttenuation: this.convertBoolModelToThree(this.get('sizeAttenuation'), 'sizeAttenuation'),
                type: this.get('type'),
            }
        );
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        MaterialModel.prototype.createPropertiesArrays.call(this);
        this.three_properties.push('map');

        this.props_created_by_three['type'] = true;

        this.property_converters['color'] = 'convertColor';
        this.property_converters['fog'] = 'convertBool';
        this.property_converters['lights'] = 'convertBool';
        this.property_converters['map'] = 'convertThreeType';
        this.property_converters['rotation'] = 'convertFloat';
        this.property_converters['sizeAttenuation'] = 'convertBool';
        this.property_converters['type'] = null;


    },

}, {

    model_name: 'SpriteMaterialModel',

    serializers: _.extend({
        map: { deserialize: serializers.unpackThreeModel },
    },  MaterialModel.serializers),
});

module.exports = {
    SpriteMaterialModel: SpriteMaterialModel,
};
