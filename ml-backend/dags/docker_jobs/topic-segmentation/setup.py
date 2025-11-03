from setuptools import setup, find_packages


setup(
    name="topic_segmentation",
    version="0.1.0",
    description="Toolkit for topic segmentation algorithms",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=["pydantic", "pyyaml", "scikit-learn", "sentence-transformers", "torch"],
)
