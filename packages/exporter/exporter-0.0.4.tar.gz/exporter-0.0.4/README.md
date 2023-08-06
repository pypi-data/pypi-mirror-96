# exporter

exporter is a simple package that helps to export Jupyter notebooks as a Python script.
Add **#export** or **# export** comments anywhere in the notebook cell you want to export as a Python script. Cells in 
the same notebook will be exported to the same Python script.

You can also export codes from Jupyter notebooks and Python scripts as an image.


# Installation

```
pip install exporter
```

Check [PyPI](https://pypi.org/project/exporter/) for all the versions available.

### Installation for Image Export Functionality
To work with image export functionality you need to install **wkhtmltopdf**.
- Ubuntu/Debian
    ```
    sudo apt-get install wkthtmltopdf
    ```
- MacOS
    ```
    brew install wkhtmltopdf
    ```
- Windows and other options

  Check [Wktmltopdf](https://wkhtmltopdf.org/downloads.html) download page.

# Basic Usage

1. Add **#export** or **# export** comments to cells you want to export.
2. 
    1. Option 1: Use command line.
          ```
          exporter notebook_path.ipynb output_path.py
          ```
          For all the options:
          ```
          exporter --help
          ```
    2. Option 2: Use Python function.
          ```python
          from exporter import export
          export("notebook_path.ipynb","oytput_path.py")
          ```

# Export Code as a Image

1. Add **# image-export-start** and **# image-export-end** comments
to the start and end of the code blocks you want to export. 
(You can export more than one code block!)
2. List all the available styles.
    ```
    image-exporter --styles
    ```
3.
    1. Option 1: Use command line.
          ```
          image-exporter script.py output_path style
          ```
          or
          ```
          image-exporter notebook.ipynb output_path style
          ```       
       For all the options:
          ```
          exporter --help
          ```
    2. Option 2: Use Python function.      
          ```python
          from exporter import image_export, available_styles
          print(available_styles())
          image_export("script.py","exported_images","colorful")
          ```

# Examples

Some examples with different styles.

emacs 
------------ 
![emacs example 0](https://github.com/hasan-yaman/exporter/raw/master/examples/example_0_emacs.jpg) 
![emacs example 1](https://github.com/hasan-yaman/exporter/raw/master/examples/example_1_emacs.jpg)

friendly
------------ 
![friendly example 0](https://github.com/hasan-yaman/exporter/raw/master/examples/example_0_friendly.jpg) 
![friendly example 1](https://github.com/hasan-yaman/exporter/raw/master/examples/example_1_friendly.jpg)

native 
------------ 
![native example 0](https://github.com/hasan-yaman/exporter/raw/master/examples/example_0_native.jpg) 
![native example 1](https://github.com/hasan-yaman/exporter/raw/master/examples/example_1_native.jpg)

vs 
------------ 
![vs example 0](https://github.com/hasan-yaman/exporter/raw/master/examples/example_0_vs.jpg) 
![vs example 1](https://github.com/hasan-yaman/exporter/raw/master/examples/example_1_vs.jpg)
