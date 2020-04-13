from setuptools import setup, find_packages
setup(
    name="bookreader2readwise",
    version="0.1",
    packages=['bookreader2readwise'],
    scripts=[],
    install_requires=["pandas"],
    package_data={},
    author="David Love",
    author_email="davidklove+github@pm.me",
    description="Converts BookReader JSON files to CSVs that can be processed by Readwise.io",
    keywords="ebook bookreader readwise",
    url="https://github.com/davidlove/bookreader2readwise",
    project_urls={
        "Source Code": "https://github.com/davidlove/bookreader2readwise",
    },
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3.0"
    ],
    entry_points={
        "console_scripts": [
            'bookreader2readwise = bookreader2readwise:run'
        ]
    }
)

