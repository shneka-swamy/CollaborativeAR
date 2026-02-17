#include "AdcNet.h"
#include <eigen3/Eigen/src/Core/Matrix.h>

// Creates an unique pointer and deletes it
template<typename... Args>
std::unique_ptr<PyObject, PyObjectDeleter> make_unique_pyobject(Args&&... args) {
    return std::unique_ptr<PyObject, PyObjectDeleter>(std::forward<Args>(args)...);
}

// Create tensor from image
torch::Tensor createTensor(cv::Mat image){
    int height = image.rows;
    int width = image.cols;
    int channels = image.channels();
    torch::Tensor tensor;
    tensor = torch::from_bolb(image.data, {height, width, channels}, torch::kByte);
    return tensor;
}

// Cast the tensor to a python object
auto castTensor(torch::Tensor tensor){
    auto casted_tensor = make_unique_pyobject(THPVariable_Wrap(tensor));
    return casted_tensor;
}

cv::Mat readImage(const char *filename){
    cv::Mat image = cv.imread(filename, cv::IMREAD_COLOR);
    return image;
}

// To open the python files and folder properly and check if that is done.
StatusHolder AdcNet::init(){
    // Must check if this is correct -- compare it with the other code
    std::string nameStr = "AdcNet";
    mName = make_unique_pyobject(PyUnicode_DecodeFSDefault(nameStr.c_str()));
    RETURN_IF_ERROR(mName.get() != NULL, Status::kDecodeFailed, "Failed to decodeFSDefault "+nameStr, true);

    mModule = make_unique_pyobject(PyImport_Import(mName.get()));
    RETURN_IF_ERROR(mModule.get() != NULL, Status::kModuleImportFailed, "Failed to import module"+nameStr, true);

    std::string funcName = "estimatePose";
    mFunc = make_unique_pyobject(PyObject_GetAttrString(mModule.get(), funcName.c_str()));
    RETURN_IF_ERROR((mFunc.get() && PyCallable_Check(mFunc.get())), Status::kFunctionImportFailed, "Cannot find function "+funcName, true);

    return StatusHolder{Status::kSuccess, "Success"}
}

// Manually destroy all the python object created.
void AdcNet::destroy(){
    mFunc.reset();
    mModule.reset();
    mName.reset();
}

StatusHolder AdcNet::determinePose(cv::Mat &image){
    torch::Tensor img_tensor = createTensor(image);
    auto img_casted = castTensor(img_tensor);
    
}