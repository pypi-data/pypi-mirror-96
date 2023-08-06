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

var PlaneModel = require('../math/Plane.autogen.js').PlaneModel;

var PlaneHelperModel = Object3DModel.extend({

    defaults: function() {
        return _.extend(Object3DModel.prototype.defaults.call(this), {

            plane: null,
            size: 1,
            color: "yellow",
            type: "PlaneHelper",

        });
    },

    constructThreeObject: function() {

        var result = new THREE.PlaneHelper(
            this.convertThreeTypeModelToThree(this.get('plane'), 'plane'),
            this.convertFloatModelToThree(this.get('size'), 'size'),
            this.convertColorModelToThree(this.get('color'), 'color')
        );
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        Object3DModel.prototype.createPropertiesArrays.call(this);
        this.three_properties.push('plane');

        this.props_created_by_three['type'] = true;
        this.props_created_by_three['matrixWorldNeedsUpdate'] = true;

        this.property_converters['plane'] = 'convertThreeType';
        this.property_converters['size'] = 'convertFloat';
        this.property_converters['color'] = 'convertColor';
        this.property_converters['type'] = null;


    },

}, {

    model_name: 'PlaneHelperModel',

    serializers: _.extend({
        plane: { deserialize: serializers.unpackThreeModel },
    },  Object3DModel.serializers),
});

module.exports = {
    PlaneHelperModel: PlaneHelperModel,
};
