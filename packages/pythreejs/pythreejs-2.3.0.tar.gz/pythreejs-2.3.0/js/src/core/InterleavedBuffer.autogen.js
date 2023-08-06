//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var Promise = require('bluebird');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');
var serializers = require('../_base/serializers');

var ThreeModel = require('../_base/Three.js').ThreeModel;


var InterleavedBufferModel = ThreeModel.extend({

    defaults: function() {
        return _.extend(ThreeModel.prototype.defaults.call(this), {

            array: undefined,
            dynamic: false,
            version: 0,
            needsUpdate: false,

        });
    },

    constructThreeObject: function() {

        var result = new THREE.InterleavedBuffer(
            this.convertArrayBufferModelToThree(this.get('array'), 'array')
        );
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        ThreeModel.prototype.createPropertiesArrays.call(this);
        this.datawidget_properties.push('array');

        this.props_created_by_three['version'] = true;
        this.props_created_by_three['needsUpdate'] = true;

        this.property_converters['array'] = 'convertArrayBuffer';
        this.property_converters['dynamic'] = 'convertBool';
        this.property_converters['version'] = null;
        this.property_converters['needsUpdate'] = 'convertBool';


    },

}, {

    model_name: 'InterleavedBufferModel',

    serializers: _.extend({
        array: dataserializers.data_union_serialization,
    },  ThreeModel.serializers),
});

module.exports = {
    InterleavedBufferModel: InterleavedBufferModel,
};
