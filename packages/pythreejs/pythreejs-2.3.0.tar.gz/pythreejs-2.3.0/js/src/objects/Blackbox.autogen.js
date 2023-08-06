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


var BlackboxModel = Object3DModel.extend({

    defaults: function() {
        return _.extend(Object3DModel.prototype.defaults.call(this), {

            type: "Blackbox",

        });
    },

    constructThreeObject: function() {

        var result = new THREE.Blackbox();
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        Object3DModel.prototype.createPropertiesArrays.call(this);

        this.props_created_by_three['type'] = true;
        this.props_created_by_three['matrixWorldNeedsUpdate'] = true;

        this.property_converters['type'] = null;


    },

}, {

    model_name: 'BlackboxModel',

    serializers: _.extend({
    },  Object3DModel.serializers),
});

module.exports = {
    BlackboxModel: BlackboxModel,
};
