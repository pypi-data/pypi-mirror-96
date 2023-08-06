#include <Python.h>
#include <stdio.h>

static PyObject* QiaoGS_show_info( PyObject *self, PyObject *args )
{ 
    const char* username[32];
    const int age;
    if(!PyArg_ParseTuple( args, "si", &username, &age )){
        return NULL;
    }

    printf("姓名:%s\n", *username );
    printf("年龄:%d\n", age );
    return Py_None;
}

static PyMethodDef QiaoGSMethods[]={
    {"show_info", QiaoGS_show_info, METH_VARARGS, "显示我的信息"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef QiaoGSModule={
    PyModuleDef_HEAD_INIT,
    "QiaoGS",
    "乔国松的个人信息",
    -1,
    QiaoGSMethods
};

PyMODINIT_FUNC PyInit_QiaoGS(void){
    return PyModule_Create(&QiaoGSModule);
}


