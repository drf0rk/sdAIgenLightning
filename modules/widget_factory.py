""" WidgetFactory Module | by ANXETY """

from IPython.display import display, HTML
import ipywidgets as widgets
import time

class WidgetFactory:
    # INIT
    def __init__(self):
        self.default_style = {'description_width': 'initial'}
        self.default_layout = widgets.Layout()

    def _validate_class_names(self, class_names):
        """Validate and normalize class names."""
        if class_names is None:
            return []
        if isinstance(class_names, str):
            return [class_names.strip()]
        if isinstance(class_names, list):
            return [cls.strip() for cls in class_names if isinstance(cls, str) and cls.strip()]
        return []

    def add_classes(self, widget, class_names):
        """Add CSS classes to a widget."""
        classes = self._validate_class_names(class_names)
        for cls in classes:
            widget.add_class(cls)

    # HTML
    def load_css(self, css_path):
        """Load CSS from a file and display it in the notebook."""
        try:
            with open(css_path, 'r', encoding='utf-8') as file:
                data = file.read()
                display(HTML(f"<style>{data}</style>"))
        except Exception as e:
            print(f"Error loading CSS from {css_path}: {e}")

    def load_js(self, js_path):
        """Load JavaScript from a file and display it in the notebook."""
        try:
            with open(js_path, 'r', encoding='utf-8') as file:
                data = file.read()
                display(HTML(f"<script>{data}</script>"))
        except Exception as e:
            print(f"Error loading JavaScript from {js_path}: {e}")

    def create_html(self, content, class_names=None):
        """Create an HTML widget with optional CSS classes."""
        html_widget = widgets.HTML(content)
        if class_names:
            self.add_classes(html_widget, class_names)
        return html_widget

    def create_header(self, name, class_names=None):
        """Create a header HTML widget."""
        class_names_str = ' '.join(self._validate_class_names(class_names)) if class_names else 'header'
        header = f'<div class="{class_names_str}">{name}</div>'
        return self.create_html(header)

    # Widgets
    def _create_widget(self, widget_type, class_names=None, **kwargs):
        """Create a widget of a specified type with optional classes and styles."""
        style = kwargs.get('style', self.default_style)
        if 'layout' not in kwargs:
             kwargs['layout'] = widgets.Layout(width='auto')

        widget = widget_type(style=style, **kwargs)
        if class_names:
            self.add_classes(widget, class_names)
        return widget

    def create_text(self, description, value='', placeholder='', class_names=None, **kwargs):
        """Create a text input widget."""
        return self._create_widget(widgets.Text, class_names=class_names, description=description, value=value, placeholder=placeholder, **kwargs)

    def create_textarea(self, description, value='', placeholder='', class_names=None, **kwargs):
        """Create a textarea input widget."""
        return self._create_widget(widgets.Textarea, class_names=class_names, description=description, value=value, placeholder=placeholder, **kwargs)

    def create_dropdown(self, options, description, value=None, placeholder='', class_names=None, **kwargs):
        """Create a dropdown widget."""
        if value is None and options: value = options[0]
        return self._create_widget(widgets.Dropdown, class_names=class_names, options=options, description=description, value=value, placeholder=placeholder, **kwargs)

    def create_select_multiple(self, options, description, value=None, class_names=None, **kwargs):
        """Create a multiple select widget."""
        if isinstance(value, str): value = (value,)
        elif value is None: value = ()
        return self._create_widget(widgets.SelectMultiple, class_names=class_names, options=options, description=description, value=value, **kwargs)
    
    def create_slider(self, value, min_val, max_val, description, class_names=None, **kwargs):
        """Create a float slider widget."""
        return self._create_widget(widgets.FloatSlider, description=description, value=value, min=min_val, max=max_val, step=0.05, readout_format='.2f', class_names=class_names, **kwargs)

    def create_checkbox(self, description, value=False, class_names=None, **kwargs):
        """Create a checkbox widget."""
        return self._create_widget(widgets.Checkbox, class_names=class_names, description=description, value=value, **kwargs)

    def create_button(self, description, class_names=None, **kwargs):
        """Create a button widget."""
        return self._create_widget(widgets.Button, class_names=class_names, description=description, **kwargs)

    def create_hbox(self, children, class_names=None, **kwargs):
        """Create a horizontal box layout for widgets."""
        return self._create_widget(widgets.HBox, children=children, class_names=class_names, **kwargs)

    def create_vbox(self, children, class_names=None, **kwargs):
        """Create a vertical box layout for widgets."""
        return self._create_widget(widgets.VBox, children=children, class_names=class_names, **kwargs)

    # Other
    def display(self, widgets_to_display):
        """Display one or multiple widgets."""
        display(widgets_to_display)

    def close(self, widgets_to_close, class_names=None, delay=0.2):
        """Close one or multiple widgets after a delay."""
        if not isinstance(widgets_to_close, list): widgets_to_close = [widgets_to_close]
        if class_names:
            for widget in widgets_to_close: self.add_classes(widget, class_names)
        time.sleep(delay)
        for widget in widgets_to_close: widget.close()

    def connect_widgets(self, widget_pairs, callbacks):
        """Connect multiple widgets to callback functions for specified property changes."""
        if not isinstance(callbacks, list): callbacks = [callbacks]
        for widget, property_name in widget_pairs:
            for callback in callbacks:
                widget.observe(lambda change, w=widget, cb=callback: cb(change, w), names=property_name)
