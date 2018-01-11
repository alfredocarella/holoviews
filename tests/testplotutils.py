from unittest import SkipTest
from nose.plugins.attrib import attr

import numpy as np

from holoviews import NdOverlay, Overlay
from holoviews.core.spaces import DynamicMap, HoloMap
from holoviews.core.options import Store, Cycle
from holoviews.element.comparison import ComparisonTestCase
from holoviews.element import (Image, Scatter, Curve, Text, Points,
                               Area, VectorField, HLine, Path)
from holoviews.operation import operation
from holoviews.plotting.util import (
    compute_overlayable_zorders, get_min_distance, process_cmap,
    initialize_dynamic, split_dmap_overlay)
from holoviews.streams import PointerX

try:
    from holoviews.plotting.bokeh import util
    bokeh_renderer = Store.renderers['bokeh']
except:
    bokeh_renderer = None


class TestOverlayableZorders(ComparisonTestCase):

    def test_compute_overlayable_zorders_holomap(self):
        hmap = HoloMap({0: Points([])})
        sources = compute_overlayable_zorders(hmap)
        self.assertEqual(sources[0], [hmap, hmap.last])

    def test_compute_overlayable_zorders_with_overlaid_holomap(self):
        points = Points([])
        hmap = HoloMap({0: points})
        curve = Curve([])
        combined = hmap*curve
        sources = compute_overlayable_zorders(combined)
        self.assertEqual(sources[0], [points, combined.last, combined])

    def test_dynamic_compute_overlayable_zorders_two_mixed_layers(self):
        area = Area(range(10))
        dmap = DynamicMap(lambda: Curve(range(10)), kdims=[])
        combined = area*dmap
        combined[()]
        sources = compute_overlayable_zorders(combined)
        self.assertEqual(sources[0], [area])
        self.assertEqual(sources[1], [dmap])

    def test_dynamic_compute_overlayable_zorders_two_mixed_layers_reverse(self):
        area = Area(range(10))
        dmap = DynamicMap(lambda: Curve(range(10)), kdims=[])
        combined = dmap*area
        combined[()]
        sources = compute_overlayable_zorders(combined)
        self.assertEqual(sources[0], [dmap])
        self.assertEqual(sources[1], [area])

    def test_dynamic_compute_overlayable_zorders_two_dynamic_layers(self):
        area = DynamicMap(lambda: Area(range(10)), kdims=[])
        dmap = DynamicMap(lambda: Curve(range(10)), kdims=[])
        combined = area*dmap
        combined[()]
        sources = compute_overlayable_zorders(combined)
        self.assertEqual(sources[0], [area])
        self.assertEqual(sources[1], [dmap])

    def test_dynamic_compute_overlayable_zorders_two_deep_dynamic_layers(self):
        area = DynamicMap(lambda: Area(range(10)), kdims=[])
        curve = DynamicMap(lambda: Curve(range(10)), kdims=[])
        area_redim = area.redim(x='x2')
        curve_redim = curve.redim(x='x2')
        combined = area_redim*curve_redim
        combined[()]
        sources = compute_overlayable_zorders(combined)
        self.assertIn(area_redim, sources[0])
        self.assertIn(area, sources[0])
        self.assertNotIn(curve_redim, sources[0])
        self.assertNotIn(curve, sources[0])
        self.assertIn(curve_redim, sources[1])
        self.assertIn(curve, sources[1])
        self.assertNotIn(area_redim, sources[1])
        self.assertNotIn(area, sources[1])

    def test_dynamic_compute_overlayable_zorders_three_deep_dynamic_layers(self):
        area = DynamicMap(lambda: Area(range(10)), kdims=[])
        curve = DynamicMap(lambda: Curve(range(10)), kdims=[])
        curve2 = DynamicMap(lambda: Curve(range(10)), kdims=[])
        area_redim = area.redim(x='x2')
        curve_redim = curve.redim(x='x2')
        curve2_redim = curve2.redim(x='x3')
        combined = area_redim*curve_redim
        combined1 = (combined*curve2_redim)
        combined1[()]
        sources = compute_overlayable_zorders(combined1)
        self.assertIn(area_redim, sources[0])
        self.assertIn(area, sources[0])
        self.assertNotIn(curve_redim, sources[0])
        self.assertNotIn(curve, sources[0])
        self.assertNotIn(curve2_redim, sources[0])
        self.assertNotIn(curve2, sources[0])

        self.assertIn(curve_redim, sources[1])
        self.assertIn(curve, sources[1])
        self.assertNotIn(area_redim, sources[1])
        self.assertNotIn(area, sources[1])
        self.assertNotIn(curve2_redim, sources[1])
        self.assertNotIn(curve2, sources[1])

        self.assertIn(curve2_redim, sources[2])
        self.assertIn(curve2, sources[2])
        self.assertNotIn(area_redim, sources[2])
        self.assertNotIn(area, sources[2])
        self.assertNotIn(curve_redim, sources[2])
        self.assertNotIn(curve, sources[2])

    def test_dynamic_compute_overlayable_zorders_three_deep_dynamic_layers_cloned(self):
        area = DynamicMap(lambda: Area(range(10)), kdims=[])
        curve = DynamicMap(lambda: Curve(range(10)), kdims=[])
        curve2 = DynamicMap(lambda: Curve(range(10)), kdims=[])
        area_redim = area.redim(x='x2')
        curve_redim = curve.redim(x='x2')
        curve2_redim = curve2.redim(x='x3')
        combined = area_redim*curve_redim
        combined1 = (combined*curve2_redim).redim(y='y2')
        combined1[()]
        sources = compute_overlayable_zorders(combined1)

        self.assertIn(area_redim, sources[0])
        self.assertIn(area, sources[0])
        self.assertNotIn(curve_redim, sources[0])
        self.assertNotIn(curve, sources[0])
        self.assertNotIn(curve2_redim, sources[0])
        self.assertNotIn(curve2, sources[0])

        self.assertIn(curve_redim, sources[1])
        self.assertIn(curve, sources[1])
        self.assertNotIn(area_redim, sources[1])
        self.assertNotIn(area, sources[1])
        self.assertNotIn(curve2_redim, sources[1])
        self.assertNotIn(curve2, sources[1])

        self.assertIn(curve2_redim, sources[2])
        self.assertIn(curve2, sources[2])
        self.assertNotIn(area_redim, sources[2])
        self.assertNotIn(area, sources[2])
        self.assertNotIn(curve_redim, sources[2])
        self.assertNotIn(curve, sources[2])

    def test_dynamic_compute_overlayable_zorders_mixed_dynamic_and_non_dynamic_overlays_reverse(self):
        area1 = Area(range(10))
        area2 = Area(range(10))
        overlay = area1 * area2
        curve = DynamicMap(lambda: Curve(range(10)), kdims=[])
        curve_redim = curve.redim(x='x2')
        combined = curve_redim*overlay
        combined[()]
        sources = compute_overlayable_zorders(combined)

        self.assertIn(curve_redim, sources[0])
        self.assertIn(curve, sources[0])
        self.assertNotIn(overlay, sources[0])

        self.assertIn(area1, sources[1])
        self.assertIn(overlay, sources[1])
        self.assertNotIn(curve_redim, sources[1])
        self.assertNotIn(curve, sources[1])

        self.assertIn(area2, sources[2])
        self.assertIn(overlay, sources[2])
        self.assertNotIn(curve_redim, sources[2])
        self.assertNotIn(curve, sources[2])

    def test_dynamic_compute_overlayable_zorders_mixed_dynamic_and_non_dynamic_ndoverlays(self):
        ndoverlay = NdOverlay({i: Area(range(10+i)) for i in range(2)})
        curve = DynamicMap(lambda: Curve(range(10)), kdims=[])
        curve_redim = curve.redim(x='x2')
        combined = ndoverlay*curve_redim
        combined[()]
        sources = compute_overlayable_zorders(combined)

        self.assertIn(ndoverlay[0], sources[0])
        self.assertIn(ndoverlay, sources[0])
        self.assertNotIn(curve_redim, sources[0])
        self.assertNotIn(curve, sources[0])

        self.assertIn(ndoverlay[1], sources[1])
        self.assertIn(ndoverlay, sources[1])
        self.assertNotIn(curve_redim, sources[1])
        self.assertNotIn(curve, sources[1])

        self.assertIn(curve_redim, sources[2])
        self.assertIn(curve, sources[2])
        self.assertNotIn(ndoverlay, sources[2])


    def test_dynamic_compute_overlayable_zorders_mixed_dynamic_and_dynamic_ndoverlay_with_streams(self):
        ndoverlay = DynamicMap(lambda x: NdOverlay({i: Area(range(10+i)) for i in range(2)}),
                               kdims=[], streams=[PointerX()])
        curve = DynamicMap(lambda: Curve(range(10)), kdims=[])
        curve_redim = curve.redim(x='x2')
        combined = ndoverlay*curve_redim
        combined[()]
        sources = compute_overlayable_zorders(combined)

        self.assertIn(ndoverlay, sources[0])
        self.assertNotIn(curve_redim, sources[0])
        self.assertNotIn(curve, sources[0])

        self.assertIn(ndoverlay, sources[1])
        self.assertNotIn(curve_redim, sources[1])
        self.assertNotIn(curve, sources[1])

        self.assertIn(curve_redim, sources[2])
        self.assertIn(curve, sources[2])
        self.assertNotIn(ndoverlay, sources[2])

    def test_dynamic_compute_overlayable_zorders_mixed_dynamic_and_dynamic_ndoverlay_with_streams_cloned(self):
        ndoverlay = DynamicMap(lambda x: NdOverlay({i: Area(range(10+i)) for i in range(2)}),
                               kdims=[], streams=[PointerX()])
        curve = DynamicMap(lambda: Curve(range(10)), kdims=[])
        curve_redim = curve.redim(x='x2')
        combined = ndoverlay*curve_redim
        combined[()]
        sources = compute_overlayable_zorders(combined.clone())

        self.assertIn(ndoverlay, sources[0])
        self.assertNotIn(curve_redim, sources[0])
        self.assertNotIn(curve, sources[0])

        self.assertIn(ndoverlay, sources[1])
        self.assertNotIn(curve_redim, sources[1])
        self.assertNotIn(curve, sources[1])

        self.assertIn(curve_redim, sources[2])
        self.assertIn(curve, sources[2])
        self.assertNotIn(ndoverlay, sources[2])

    def test_dynamic_compute_overlayable_zorders_mixed_dynamic_and_non_dynamic_ndoverlays_reverse(self):
        ndoverlay = NdOverlay({i: Area(range(10+i)) for i in range(2)})
        curve = DynamicMap(lambda: Curve(range(10)), kdims=[])
        curve_redim = curve.redim(x='x2')
        combined = curve_redim*ndoverlay
        combined[()]
        sources = compute_overlayable_zorders(combined)

        self.assertIn(curve_redim, sources[0])
        self.assertIn(curve, sources[0])
        self.assertNotIn(ndoverlay, sources[0])

        self.assertIn(ndoverlay[0], sources[1])
        self.assertIn(ndoverlay, sources[1])
        self.assertNotIn(curve_redim, sources[1])
        self.assertNotIn(curve, sources[1])

        self.assertIn(ndoverlay[1], sources[2])
        self.assertIn(ndoverlay, sources[2])
        self.assertNotIn(curve_redim, sources[2])
        self.assertNotIn(curve, sources[2])

    def test_dynamic_compute_overlayable_zorders_three_deep_dynamic_layers_reduced(self):
        area = DynamicMap(lambda: Area(range(10)), kdims=[])
        curve = DynamicMap(lambda: Curve(range(10)), kdims=[])
        curve2 = DynamicMap(lambda: Curve(range(10)), kdims=[])
        area_redim = area.redim(x='x2')
        curve_redim = curve.redim(x='x2')
        curve2_redim = curve2.redim(x='x3')
        combined = (area_redim*curve_redim).map(lambda x: x.get(0), Overlay)
        combined1 = combined*curve2_redim
        combined1[()]
        sources = compute_overlayable_zorders(combined1)

        self.assertIn(curve_redim, sources[0])
        self.assertIn(curve, sources[0])
        self.assertIn(area_redim, sources[0])
        self.assertIn(area, sources[0])
        self.assertNotIn(curve2_redim, sources[0])
        self.assertNotIn(curve2, sources[0])

        self.assertIn(curve2_redim, sources[1])
        self.assertIn(curve2, sources[1])
        self.assertNotIn(area_redim, sources[1])
        self.assertNotIn(area, sources[1])
        self.assertNotIn(curve_redim, sources[1])
        self.assertNotIn(curve, sources[1])


    def test_dynamic_compute_overlayable_zorders_three_deep_dynamic_layers_reduced_layers_by_one(self):
        area = DynamicMap(lambda: Area(range(10)), kdims=[])
        area2 = DynamicMap(lambda: Area(range(10)), kdims=[])
        curve = DynamicMap(lambda: Curve(range(10)), kdims=[])
        curve2 = DynamicMap(lambda: Curve(range(10)), kdims=[])
        area_redim = area.redim(x='x2')
        curve_redim = curve.redim(x='x2')
        curve2_redim = curve2.redim(x='x3')
        combined = (area_redim*curve_redim*area2).map(lambda x: x.clone(x.items()[:2]), Overlay)
        combined1 = combined*curve2_redim
        combined1[()]
        sources = compute_overlayable_zorders(combined1)

        self.assertNotIn(curve_redim, sources[0])
        self.assertNotIn(curve, sources[0])
        self.assertNotIn(curve2_redim, sources[0])
        self.assertNotIn(curve2, sources[0])
        self.assertNotIn(area, sources[0])
        self.assertNotIn(area_redim, sources[0])
        self.assertNotIn(area2, sources[0])

        self.assertNotIn(area_redim, sources[1])
        self.assertNotIn(area, sources[1])
        self.assertNotIn(curve2_redim, sources[1])
        self.assertNotIn(curve2, sources[1])
        self.assertNotIn(area2, sources[0])

        self.assertIn(curve2_redim, sources[2])
        self.assertIn(curve2, sources[2])
        self.assertNotIn(area_redim, sources[2])
        self.assertNotIn(area, sources[2])
        self.assertNotIn(area2, sources[0])
        self.assertNotIn(curve_redim, sources[2])
        self.assertNotIn(curve, sources[2])


class TestSplitDynamicMapOverlay(ComparisonTestCase):
    """
    Tests the split_dmap_overlay utility
    """

    def setUp(self):
        self.dmap_element = DynamicMap(lambda: Image([]))
        self.dmap_overlay = DynamicMap(lambda: Overlay([Curve([]), Points([])]))
        self.dmap_ndoverlay = DynamicMap(lambda: NdOverlay({0: Curve([]), 1: Curve([])}))
        self.element = Scatter([])
        self.el1, self.el2 = Path([]), HLine(0)
        self.overlay = Overlay([self.el1, self.el2])
        self.ndoverlay = NdOverlay({0: VectorField([]), 1: VectorField([])})

    def test_dmap_ndoverlay(self):
        test = self.dmap_ndoverlay
        initialize_dynamic(test)
        layers = [self.dmap_ndoverlay, self.dmap_ndoverlay]
        self.assertEqual(split_dmap_overlay(test), layers)

    def test_dmap_overlay(self):
        test = self.dmap_overlay
        initialize_dynamic(test)
        layers = [self.dmap_overlay, self.dmap_overlay]
        self.assertEqual(split_dmap_overlay(test), layers)

    def test_dmap_element_mul_dmap_overlay(self):
        test = self.dmap_element * self.dmap_overlay
        initialize_dynamic(test)
        layers = [self.dmap_element, self.dmap_overlay, self.dmap_overlay]
        self.assertEqual(split_dmap_overlay(test), layers)

    def test_dmap_element_mul_dmap_ndoverlay(self):
        test = self.dmap_element * self.dmap_ndoverlay
        initialize_dynamic(test)
        layers = [self.dmap_element, self.dmap_ndoverlay]
        self.assertEqual(split_dmap_overlay(test), layers)

    def test_dmap_element_mul_element(self):
        test = self.dmap_element * self.element
        initialize_dynamic(test)
        layers = [self.dmap_element, self.element]
        self.assertEqual(split_dmap_overlay(test), layers)

    def test_dmap_element_mul_overlay(self):
        test = self.dmap_element * self.overlay
        initialize_dynamic(test)
        layers = [self.dmap_element, self.el1, self.el2]
        self.assertEqual(split_dmap_overlay(test), layers)

    def test_dmap_element_mul_ndoverlay(self):
        test = self.dmap_element * self.ndoverlay
        initialize_dynamic(test)
        layers = [self.dmap_element, self.ndoverlay]
        self.assertEqual(split_dmap_overlay(test), layers)

    def test_dmap_overlay_mul_dmap_ndoverlay(self):
        test = self.dmap_overlay * self.dmap_ndoverlay
        initialize_dynamic(test)
        layers = [self.dmap_overlay, self.dmap_overlay, self.dmap_ndoverlay]
        self.assertEqual(split_dmap_overlay(test), layers)

    def test_dmap_overlay_mul_element(self):
        test = self.dmap_overlay * self.element
        initialize_dynamic(test)
        layers = [self.dmap_overlay, self.dmap_overlay, self.element]
        self.assertEqual(split_dmap_overlay(test), layers)

    def test_dmap_overlay_mul_overlay(self):
        test = self.dmap_overlay * self.overlay
        initialize_dynamic(test)
        layers = [self.dmap_overlay, self.dmap_overlay, self.el1, self.el2]
        self.assertEqual(split_dmap_overlay(test), layers)

    def test_dmap_all_combinations(self):
        test = (self.dmap_overlay * self.element * self.dmap_ndoverlay *
                self.overlay * self.dmap_element * self.ndoverlay)
        initialize_dynamic(test)
        layers = [self.dmap_overlay, self.dmap_overlay, self.element,
                  self.dmap_ndoverlay, self.el1, self.el2, self.dmap_element,
                  self.ndoverlay]
        self.assertEqual(split_dmap_overlay(test), layers)

    def test_dmap_overlay_operation_mul_dmap_ndoverlay(self):
        mapped = operation(self.dmap_overlay)
        test = mapped * self.dmap_ndoverlay
        initialize_dynamic(test)
        layers = [mapped, mapped, self.dmap_ndoverlay]
        self.assertEqual(split_dmap_overlay(test), layers)

    def test_dmap_overlay_linked_operation_mul_dmap_ndoverlay(self):
        mapped = operation(self.dmap_overlay, link_inputs=True)
        test = mapped * self.dmap_ndoverlay
        initialize_dynamic(test)
        layers = [mapped, mapped, self.dmap_ndoverlay]
        self.assertEqual(split_dmap_overlay(test), layers)

    def test_dmap_overlay_linked_operation_mul_dmap_ndoverlay(self):
        mapped = self.dmap_overlay.map(lambda x: x.get(0), Overlay)
        test = mapped * self.element * self.dmap_ndoverlay
        initialize_dynamic(test)
        layers = [mapped, self.element, self.dmap_ndoverlay]
        self.assertEqual(split_dmap_overlay(test), layers)


class TestPlotColorUtils(ComparisonTestCase):

    def test_process_cmap_mpl(self):
        colors = process_cmap('Greys', 3)
        self.assertEqual(colors, ['#ffffff', '#959595', '#000000'])

    
    def test_process_cmap_instance_mpl(self):
        try:
            from matplotlib.cm import get_cmap
        except:
            raise SkipError("Matplotlib needed to test matplotlib colormap instances")
        cmap = get_cmap('Greys')
        colors = process_cmap(cmap, 3)
        self.assertEqual(colors, ['#ffffff', '#959595', '#000000'])

    def test_process_cmap_bokeh(self):
        colors = process_cmap('Category20', 3)
        self.assertEqual(colors, ['#1f77b4', '#aec7e8', '#ff7f0e'])

    def test_process_cmap_list_cycle(self):
        colors = process_cmap(['#ffffff', '#959595', '#000000'], 4)
        self.assertEqual(colors, ['#ffffff', '#959595', '#000000', '#ffffff'])

    def test_process_cmap_cycle(self):
        colors = process_cmap(Cycle(values=['#ffffff', '#959595', '#000000']), 4)
        self.assertEqual(colors, ['#ffffff', '#959595', '#000000', '#ffffff'])

    def test_process_cmap_invalid_str(self):
        with self.assertRaises(ValueError):
            colors = process_cmap('NonexistentColorMap', 3)

    def test_process_cmap_invalid_type(self):
        with self.assertRaises(TypeError):
            colors = process_cmap({'A', 'B', 'C'}, 3)


class TestPlotUtils(ComparisonTestCase):

    def test_get_min_distance_float32_type(self):
        xs, ys = (np.arange(0, 2., .2, dtype='float32'),
                  np.arange(0, 2., .2, dtype='float32'))
        X, Y = np.meshgrid(xs, ys)
        dist = get_min_distance(Points((X.flatten(), Y.flatten())))
        self.assertEqual(round(dist, 5), 0.2)

    def test_get_min_distance_int32_type(self):
        xs, ys = (np.arange(0, 10, dtype='int32'),
                  np.arange(0, 10, dtype='int32'))
        X, Y = np.meshgrid(xs, ys)
        dist = get_min_distance(Points((X.flatten(), Y.flatten())))
        self.assertEqual(dist, 1.0)


@attr(optional=1)  # Flexx is optional
class TestBokehUtils(ComparisonTestCase):

    def setUp(self):
        if not bokeh_renderer:
            raise SkipTest("Bokeh required to test bokeh plot utils.")


    def test_py2js_funcformatter_single_arg(self):
        def test(x):  return '%s$' % x
        jsfunc = util.py2js_tickformatter(test)
        js_func = ('var x = tick;\nvar formatter;\nformatter = function () {\n'
                   '    return "" + x + "$";\n};\n\nreturn formatter();\n')
        self.assertEqual(jsfunc, js_func)


    def test_py2js_funcformatter_two_args(self):
        def test(x, pos):  return '%s$' % x
        jsfunc = util.py2js_tickformatter(test)
        js_func = ('var x = tick;\nvar formatter;\nformatter = function () {\n'
                   '    return "" + x + "$";\n};\n\nreturn formatter();\n')
        self.assertEqual(jsfunc, js_func)


    def test_py2js_funcformatter_arg_and_kwarg(self):
        def test(x, pos=None):  return '%s$' % x
        jsfunc = util.py2js_tickformatter(test)
        js_func = ('var x = tick;\nvar formatter;\nformatter = function () {\n'
                   '    pos = (pos === undefined) ? null: pos;\n    return "" '
                   '+ x + "$";\n};\n\nreturn formatter();\n')
        self.assertEqual(jsfunc, js_func)
