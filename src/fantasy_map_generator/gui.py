"""Web-based GUI for interactive map generation.

Planned components:
- Flask web app
- Parameter adjustment sliders (seed, terrain density, etc.)
- Real-time SVG preview
- Map configuration editor
- Export to PNG/SVG

Usage:
    python -m fantasy_map_generator.gui
"""

try:
    import flask
except ImportError:
    flask = None


def create_app():
    """Create and configure the Flask application.

    Returns:
        Flask app instance.

    Raises:
        ImportError: If Flask is not installed.
    """
    if flask is None:
        raise ImportError(
            "Flask is required for the GUI. Install with: pip install fantasy-map-generator[gui]"
        )

    app = flask.Flask(__name__)

    @app.route("/")
    def index():
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Fantasy Map Generator</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body { font-family: sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
                .container { max-width: 1200px; margin: 0 auto; }
                h1 { color: #333; }
                .status { padding: 10px; background: #e3f2fd; border-radius: 4px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Fantasy Map Generator</h1>
                <div class="status">
                    Web GUI is under development. For now, use the CLI:
                    <code>python -m fantasy_map_generator --help</code>
                </div>
            </div>
        </body>
        </html>
        """

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
