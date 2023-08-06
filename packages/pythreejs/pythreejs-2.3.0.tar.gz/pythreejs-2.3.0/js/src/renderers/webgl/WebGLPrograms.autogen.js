//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var Promise = require('bluebird');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');
var serializers = require('../../_base/serializers');

var ThreeModel = require('../../_base/Three.js').ThreeModel;


var WebGLProgramsModel = ThreeModel.extend({

    defaults: function() {
        return _.extend(ThreeModel.prototype.defaults.call(this), {


        });
    },

    constructThreeObject: function() {

        var result = new THREE.WebGLPrograms();
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        ThreeModel.prototype.createPropertiesArrays.call(this);




    },

}, {

    model_name: 'WebGLProgramsModel',

    serializers: _.extend({
    },  ThreeModel.serializers),
});

module.exports = {
    WebGLProgramsModel: WebGLProgramsModel,
};
