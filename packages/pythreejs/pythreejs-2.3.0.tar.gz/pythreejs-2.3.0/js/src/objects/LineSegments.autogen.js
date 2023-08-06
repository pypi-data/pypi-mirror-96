//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var Promise = require('bluebird');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');
var serializers = require('../_base/serializers');

var LineModel = require('./Line.autogen.js').LineModel;


var LineSegmentsModel = LineModel.extend({

    defaults: function() {
        return _.extend(LineModel.prototype.defaults.call(this), {

            type: "LineSegments",

        });
    },

    constructThreeObject: function() {

        var result = new THREE.LineSegments(
            this.convertThreeTypeModelToThree(this.get('geometry'), 'geometry'),
            this.convertThreeTypeModelToThree(this.get('material'), 'material')
        );
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        LineModel.prototype.createPropertiesArrays.call(this);

        this.props_created_by_three['type'] = true;
        this.props_created_by_three['matrixWorldNeedsUpdate'] = true;

        this.property_converters['type'] = null;


    },

}, {

    model_name: 'LineSegmentsModel',

    serializers: _.extend({
    },  LineModel.serializers),
});

module.exports = {
    LineSegmentsModel: LineSegmentsModel,
};
