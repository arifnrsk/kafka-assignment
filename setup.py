"""
Setup configuration for Kafka Assignment
"""
from setuptools import setup, find_packages

# Read requirements from requirements.txt
def read_requirements():
    with open('requirements.txt', 'r') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

# Read README for long description
def read_readme():
    try:
        with open('README.md', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Kafka Producer-Consumer Assignment for Data Engineering Bootcamp"

setup(
    name="kafka-assignment",
    version="1.0.0",
    description="Kafka Producer-Consumer Assignment for Data Engineering Bootcamp",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="Data Engineer Bootcamp Student",
    author_email="student@bootcamp.com",
    url="https://github.com/arifnrsk/kafka-assignment",
    
    # Package configuration
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    
    # Dependencies
    install_requires=read_requirements(),
    
    # Optional dependencies
    extras_require={
        'dev': [
            'pytest>=7.4.0',
            'pytest-cov>=4.1.0',
            'black>=23.7.0',
            'flake8>=6.0.0',
            'isort>=5.12.0'
        ]
    },
    
    # Entry points
    entry_points={
        'console_scripts': [
            'kafka-producer=producer.event_producer:main',
            'kafka-consumer=consumer.event_consumer:main',
        ],
    },
    
    # Classifiers
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Distributed Computing",
    ],
    
    # Python version requirement
    python_requires=">=3.8",
    
    # Include additional files
    include_package_data=True,
    
    # Package metadata
    keywords="kafka, producer, consumer, data-engineering, bootcamp",
    project_urls={
        "Bug Reports": "https://github.com/arifnrsk/kafka-assignment/issues",
        "Source": "https://github.com/arifnrsk/kafka-assignment",
        "Documentation": "https://github.com/arifnrsk/kafka-assignment/blob/main/README.md",
    },
) 