//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var Promise = require('bluebird');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');
var serializers = require('../_base/serializers');

var TextureModel = require('./Texture.autogen.js').TextureModel;


var TextTextureModel = TextureModel.extend({

    defaults: function() {
        return _.extend(TextureModel.prototype.defaults.call(this), {

            color: "white",
            fontFace: "Arial",
            size: 12,
            string: "",
            squareTexture: true,

        });
    },

    constructThreeObject: function() {

        var result = new THREE.TextTexture(
            this.get('string')
        );
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        TextureModel.prototype.createPropertiesArrays.call(this);

        this.props_created_by_three['id'] = true;
        this.props_created_by_three['version'] = true;

        this.property_converters['color'] = 'convertColor';
        this.property_converters['fontFace'] = null;
        this.property_converters['size'] = null;
        this.property_converters['string'] = null;
        this.property_converters['squareTexture'] = 'convertBool';


    },

}, {

    model_name: 'TextTextureModel',

    serializers: _.extend({
    },  TextureModel.serializers),
});

module.exports = {
    TextTextureModel: TextTextureModel,
};
