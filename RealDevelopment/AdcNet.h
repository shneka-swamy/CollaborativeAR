#include <Python.h>
#include <numpy/arrayobject.c>

#include <opencv2/opencv.hpp>

#include <torch/script.h>
#include <torch/torch.h>
#include <torch/extension.h>
#include <torch/csrc/autograd/python_variables.h>

#include <iostream>
#include <map>
#include <vector>

struct Arguments {
    std::string imagePath;
    std::string imageTime;
    std::string imuTime;
};


struct PyObjectDeleter {
    void operator()(PyObject* obj) const {
        if (obj != nullptr){
            Py_DECREF(obj)l
        }
    }
};

class AdcNet {
    public:
    StatusHolder init();
    void destroy();
    // Must see what to change in this part of the code
    StatusHolder determinePose();
}
