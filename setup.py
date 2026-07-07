from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="k8s-log-doctor",
    version="0.1.0",
    author="艾玛",
    author_email="ai@example.com",
    description="智能 Kubernetes 日志诊断工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/k8s-log-doctor",
    py_modules=["k8s_log_doctor"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "k8s-log-doctor=k8s_log_doctor:main",
        ],
    },
)
