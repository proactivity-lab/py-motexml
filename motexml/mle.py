"""mle.py: MoteXML encoder."""
import ctypes

__author__ = "Raido Pahtma"
__license__ = "MIT"

libname = "libmlformat.so"
lib = ctypes.cdll.LoadLibrary(libname)
lib.MLO_getBuffer.restype = ctypes.POINTER(ctypes.c_char)


class MLObject(object):

    def __init__(self, cobject = None):
        if cobject is None:
            self.index = 0
            self.type = 0
            self.value = None
            self.valueIsPresent = False
            self.subject = 0
            self.buffer = None
            self.bufferLength = 0

        else:
            self.index = lib.MLO_getIndex(cobject)
            self.type = lib.MLO_getType(cobject)
            self.value = lib.MLO_getValue(cobject)
            self.valueIsPresent = lib.MLO_getValueIsPresent(cobject)
            self.subject = lib.MLO_getSubject(cobject)
            self.bufferLength = lib.MLO_getBufferLength(cobject)
            if self.bufferLength > 0:
                bufstring = ctypes.string_at(lib.MLO_getBuffer(cobject), self.bufferLength)
                self.buffer = ctypes.create_string_buffer(bufstring, self.bufferLength)
            else:
                self.buffer = None

    def setValue(self, value):
        if value is None:
            self.valueIsPresent = False
        else:
            self.valueIsPresent = True
        self.value = value

    def getBuffer(self):
        return ctypes.string_at(self.buffer, self.bufferLength)

    # the buffer is expected to be a raw string
    def setBuffer(self, bufstring, length):
        self.bufferLength = length
        self.buffer = ctypes.create_string_buffer(bufstring, length)

    def clearBuffer(self):
        self.buffer = None
        self.bufferLength = 0

    # Note that the buffer of the cObject is only valid as long as the MLObject exists,
    # so don't lose that reference!
    def cObject(self):
        cobject = ctypes.create_string_buffer(lib.MLO_objectSize())
        lib.MLO_setType(cobject, self.type)
        lib.MLO_setSubject(cobject, self.subject)
        lib.MLO_setValue(cobject, self.value)
        lib.MLO_setValueIsPresent(cobject, self.valueIsPresent)
        lib.MLO_setBuffer(cobject, self.buffer, self.bufferLength)
        return cobject


class MLE(object):

    def __init__(self, size=512):
        """ml encoder initialization."""
        self._enc = ctypes.create_string_buffer(lib.MLE_encoderSize())
        self._buffer = ctypes.create_string_buffer(size)
        lib.MLE_initialize(self._enc, self._buffer, size)

    def appendObject(self, mlobject):
        return lib.MLE_appendObject(self._enc, mlobject.cObject())

    def appendOSV(self, object, subject, value):
        return lib.MLE_appendOSV(self._enc, object, subject, value)

    def appendOS(self, object, subject):
        return lib.MLE_appendOS(self._enc, object, subject)

    def str(self):
        """finalize and return buffer"""
        size = lib.MLE_finalize(self._enc)
        return self._buffer[0:size]


class MLI(object):

    def __init__(self, buffer):
        """ml iterator initilization."""
        self._iter = ctypes.create_string_buffer(lib.MLI_iteratorSize())
        self._buffer = ctypes.create_string_buffer(buffer)
        self._length = len(buffer)
        lib.MLI_initialize(self._iter, self._buffer, self._length)

    def next(self):
        cobject = ctypes.create_string_buffer(lib.MLO_objectSize())

        ndex = lib.MLI_next(self._iter, cobject)
        if ndex > 0:
            object = MLObject(cobject)
            return object

        return None

    def nextWithSubject(self, subject):
        cobject = ctypes.create_string_buffer(lib.MLO_objectSize())

        ndex = lib.MLI_nextWithSubject(self._iter, subject, cobject)
        if ndex > 0:
            object = MLObject(cobject)
            return object

        return None

    def reset(self):
        return lib.MLI_reset(self._iter)
