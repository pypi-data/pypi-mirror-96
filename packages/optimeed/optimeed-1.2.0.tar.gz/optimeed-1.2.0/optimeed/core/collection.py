import copy
import json
import os
from abc import abstractmethod, ABCMeta
from threading import Timer, Lock

from optimeed.core.tools import getPath_workspace, delete_indices_from_list
from .myjson import obj_to_json, json_to_obj, json_to_obj_safe, encode_str_json, decode_str_json, get_json_module_tree_from_dict, MODULE_TAG, CLASS_TAG
from .tools import indentParagraph, rgetattr, printIfShown, SHOW_WARNING, SHOW_DEBUG, SHOW_INFO  # , applyEquation
import re
import inspect
from shutil import rmtree
from math import floor

try:
    import pandas as pd
    has_pandas = True
except ImportError:
    has_pandas = False


class DataStruct_Interface(metaclass=ABCMeta):
    def __init__(self):
        self.info = ''

    @abstractmethod
    def save(self, filename):
        """Save the datastructure to filename"""
        pass

    @staticmethod
    @abstractmethod
    def load(filename, **kwargs):
        """Load the datastructure from filename"""
        pass

    def get_info(self):
        """Get simple string describing the datastructure"""
        return self.info

    def set_info(self, info):
        """Set simple string describing the datastructure"""
        self.info = info

    @staticmethod
    def get_extension():
        """File extension used for datastructure"""
        return ".json"

    def __str__(self):
        return "DataStruct: {}".format(str(self.info))


class ListDataStruct_Interface(DataStruct_Interface, metaclass=ABCMeta):
    @abstractmethod
    def add_data(self, data_in):
        pass

    @abstractmethod
    def get_data_at_index(self, index):
        pass

    @abstractmethod
    def get_data_generator(self):
        pass

    @staticmethod
    def _recursive_apply_moduleTree(nestedTree, nestedObject):
        for key in nestedTree:
            if key == CLASS_TAG or key == MODULE_TAG:
                try:
                    nestedObject[key] = nestedTree[key]
                except TypeError as e:
                    printIfShown("(following error when loading, might come from numpy elementary types) {}".format(e), SHOW_DEBUG)
            else:
                if isinstance(nestedObject, dict):
                    ListDataStruct._recursive_apply_moduleTree(nestedTree[key], nestedObject[key])

    @staticmethod
    def _jsondata_to_obj(item, theClass=None):
        return json_to_obj(item) if theClass is None else json_to_obj_safe(item, theClass)

    def get_list_attributes(self, attributeName):
        """
        Get the value of attributeName of all the data in the Collection

        :param attributeName: string (name of the attribute to get)
        :return: list
        """
        if not attributeName:
            return list()
        return [rgetattr(data, attributeName) for data in self.get_data_generator()]


class AutosaveStruct:
    """Structure that provides automated save of DataStructures"""

    def __init__(self, dataStruct, filename='', change_filename_if_exists=True):
        if not filename:
            self.filename = getPath_workspace() + '/default_collection'
        else:
            self.filename = os.path.abspath(filename)

        self.theDataStruct = dataStruct

        self.set_filename(self.filename, change_filename_if_exists)
        self.timer = None

    def __str__(self):
        return str(self.theDataStruct)

    def get_filename(self):
        """Get set filename"""
        return self.filename

    def set_filename(self, filename, change_filename_if_exists):
        """

        :param filename: Filename to set
        :param change_filename_if_exists: If already exists, create a new filename
        """
        if not filename.endswith(self.theDataStruct.get_extension()):
            filename += self.theDataStruct.get_extension()

        if change_filename_if_exists:
            curr_index = 1
            head, tail = os.path.split(filename)
            base_name = os.path.splitext(tail)[0]
            while os.path.exists(filename):
                filename = head + '/' + base_name + '_' + str(curr_index) + self.theDataStruct.get_extension()
                curr_index += 1
        self.filename = filename

    def stop_autosave(self):
        """Stop autosave"""
        if self.timer is not None:
            self.timer.cancel()

    def start_autosave(self, timer_autosave, safe_save=True):
        """Start autosave"""
        self.save(safe_save=safe_save)
        if timer_autosave > 0:
            self.timer = Timer(timer_autosave, lambda: self.start_autosave(timer_autosave, safe_save=safe_save))
            self.timer.daemon = True
            self.timer.start()

    def save(self, safe_save=True):
        """Save"""
        if not os.path.exists(os.path.dirname(self.filename)):
            os.makedirs(os.path.dirname(self.filename))

        if os.path.exists(self.filename) and safe_save:
            temp_file = self.filename + 'temp'
            self.theDataStruct.save(temp_file)
            try:
                os.replace(temp_file, self.filename)
            except FileNotFoundError:
                pass
        else:
            self.theDataStruct.save(self.filename)

    def get_datastruct(self):
        """Return :class:'~DataStruct_Interface'"""
        return self.theDataStruct

    def __getstate__(self):
        state = self.__dict__.copy()
        del state["timer"]
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.timer = None


class ListDataStruct(ListDataStruct_Interface):
    _INFO_STR = "info"
    _DATA_STR = "data"
    _COMPRESS_SAVE_STR = "module_tree"

    def __init__(self, compress_save=False):
        """
        Structure of data containing a single list of objects.

        :param compress_save: Set to True if all the data have the same class and module names, so that emitted file is more efficient
        """
        super().__init__()
        self.theData = list()
        self.compress_save = compress_save
        self.json_module_tree = ''

    def __len__(self):
        return self.get_length()

    def get_length(self):
        return len(self.theData)

    def save(self, filename):
        """Save data using json format. The data to be saved are automatically detected, see :meth:`~optimeed.core.myjson.obj_to_json` """
        theStr = self._format_str_save()
        with open(filename, "w", encoding='utf-8') as f:
            f.write(theStr)

    def _format_str_save(self):
        """Save data using json format. The data to be saved are automatically detected, see :meth:`~optimeed.core.myjson.obj_to_json` """
        theStr = self._format_header_info_lines()
        theStr += '\t"{}": \n{}'.format(ListDataStruct._DATA_STR, indentParagraph(self._format_data_lines(), 3))
        theStr += self._format_tail_lines()
        return theStr

    def _format_header_info_lines(self):
        return '{{\n\t"{}": "{}",\n'.format(ListDataStruct._INFO_STR, encode_str_json(self.get_info()))

    def _format_data_lines(self):
        # Format data as json object
        listStr = "[\n"
        for k, item in enumerate(self.get_data_generator()):
            obj_str = "\t" + json.dumps(obj_to_json(item))
            # if compress save: remove all information relative to module and class
            if self.compress_save:
                obj_str = re.sub("\s*\"__module__\" *: *(\"(.*?)\"(,|\s|)|\s*\{(.*?)\}(,|\s|))", '', obj_str)
                obj_str = re.sub("\s*\"__class__\" *: *(\"(.*?)\"(,|\s|)|\s*\{(.*?)\}(,|\s|))", '', obj_str)

            if k < self.get_length() - 1:
                obj_str += ",\n"
            listStr += obj_str
        listStr += "\n]"

        return listStr

    def _get_json_module_tree(self):
        if not self.json_module_tree and len(self.theData):
            new_module_tree = json.dumps(get_json_module_tree_from_dict(obj_to_json(self.theData[-1])))
            if len(new_module_tree) > len(self.json_module_tree):
                self.json_module_tree = new_module_tree

    def _format_tail_lines(self):
        theStr = ''
        # if compress save: add module and class tree at end of file
        if self.compress_save:
            self._get_json_module_tree()
            theStr += '\t,"{}": {}\n'.format(ListDataStruct._COMPRESS_SAVE_STR, self.json_module_tree)
        # Terminates
        theStr += "}"
        return theStr

    @staticmethod
    def load(filename, theClass=None):
        """
        Load the file filename.

        :param filename: file to load
        :param theClass: optional. Can be used to fix unpickling errors.
        :return: self-like object
        """
        if filename:
            if not os.path.splitext(filename)[-1].lower():
                filename += ListDataStruct.get_extension()

            try:
                newStruct = ListDataStruct()
                with open(filename, 'r', encoding="utf-8", newline="\n") as f:
                    theDict = json.load(f)
                newStruct.set_info(decode_str_json(theDict[ListDataStruct._INFO_STR]))

                # If datastruct has been compressed,
                try:
                    theModuleTree = theDict[ListDataStruct._COMPRESS_SAVE_STR]
                    for item in theDict[ListDataStruct._DATA_STR]:
                        ListDataStruct._recursive_apply_moduleTree(theModuleTree, item)
                except KeyError:
                    pass

                if theClass is not None:
                    theData = [json_to_obj_safe(item, theClass) for item in theDict[ListDataStruct._DATA_STR]]
                else:
                    theData = [json_to_obj(item) for item in theDict[ListDataStruct._DATA_STR]]
                newStruct.set_data(theData)
                return newStruct
            # except TypeError as e:

            # printIfShown("{}, recommended to use theclass keyword in method load".format(e), SHOW_WARNING)
            except OSError:
                printIfShown("Could not read file ! " + filename, SHOW_WARNING)
            except EOFError:
                printIfShown("File empty ! " + filename, SHOW_WARNING)
        else:
            printIfShown("INVALID COLLECTION FILENAME: " + filename, SHOW_WARNING)

    def add_data(self, data_in):
        """Add a data to the list"""
        self.theData.append(copy.deepcopy(data_in))

    def get_data(self):
        """Get full list of datas"""
        printIfShown("get_data() deprecated! Please use get_data_at_index or get_data_generator whenever possible", SHOW_WARNING)
        inspect.stack()
        return self.theData

    def get_data_generator(self):
        """Get a generator to all the data stored"""
        for k in range(len(self)):
            yield self.get_data_at_index(k)

    def get_data_at_index(self, index):
        return self.theData[index]

    def set_data(self, theData):
        """Set full list of datas"""
        self.theData = theData

    def set_data_at_index(self, data_in, index):
        """Replace data at specific index"""
        self.theData[index] = data_in

    # def set_attribute_data(self, the_attribute, the_value):
    #     """Set attribute to all data"""
    #     for item in self.get_data():
    #         setattr(item, the_attribute, the_value)
    #
    # def set_attribute_equation(self, attribute_name, equation_str):
    #     """
    #     Advanced method to set the value of attribute_name from equation_str
    #
    #     :param attribute_name: string (name of the attribute to set)
    #     :param equation_str: formatted equation, check :meth:`~optimeed.core.CommonFunctions_Library.applyEquation`
    #     :return:
    #     """
    #     for item in self.get_data():
    #         setattr(item, attribute_name, applyEquation(item, equation_str))

    def reset_data(self):
        self.theData = list()

    def delete_points_at_indices(self, indices):
        """
        Delete several elements from the Collection

        :param indices: list of indices to delete
        """
        for index in sorted(indices, reverse=True):
            del self.get_data()[index]

    def export_xls(self, excelFilename, excelsheet='Sheet1', mode='w'):
        """Export the collection to excel. It only exports the direct attributes.

        :param excelFilename: filename of the excel
        :param excelsheet: name of the sheet
        :param mode: 'w' to erase existing file, 'a' to append sheetname to existing file
        """
        if has_pandas:
            if len(self.get_data()):
                attributes = list(vars(self.get_data_at_index(0)).keys())
                dictToExport = dict()
                for attribute in attributes:
                    dictToExport[attribute] = [float(rgetattr(item, attribute)) for item in self.get_data_generator()]

                writer = pd.ExcelWriter(excelFilename)
                if mode == 'a':
                    try:
                        alldata = pd.read_excel(excelFilename, sheet_name=None)
                        for key in alldata:
                            alldata[key].to_excel(writer, sheet_name=key, index=False)
                    except FileNotFoundError:
                        pass
                df = pd.DataFrame(dictToExport)
                df.to_excel(writer, sheet_name=excelsheet, index=False)
                writer.save()
        else:
            printIfShown("Failed to import pandas. Excel export will fail.", SHOW_WARNING)

    def merge(self, collection):
        """
        Merge a collection with the current collection

        :param collection: :class:`~optimeed.core.Collection.Collection` to merge
        """
        for item in collection.get_data():
            self.add_data(item)


class Memory_efficient_ListDataStruct(ListDataStruct):
    def __init__(self, *args, **kwargs):
        """
        This class is an extension to the classical :class:`ListDataStruct`.
        It is designed to be particularly memory-efficient by dumping its content each time :meth:`save`is called.
        Each new data is added to a data_buffer meanwhile.
        This increases the disk usage and lowers the RAM usage
        """
        super().__init__(*args, **kwargs)
        self.number_of_elements_in_file = 0
        self.initial_filename = None
        self.data_buffer = list()
        self.indices_to_delete = list()

    def save(self, filename):
        if not len(self.data_buffer):
            return
        if not self.initial_filename:
            open(filename, 'w').close()

        with open(filename, "r+", encoding='utf-8') as f:
            numberLinesBeforeData = self._format_header_info_lines().count("\n") + 2

            existing_data_lines = list()
            for i, line in enumerate(f):
                if numberLinesBeforeData <= i < numberLinesBeforeData + self.number_of_elements_in_file:
                    if not line.isspace():
                        existing_data_lines.append(line.strip())
            f.seek(0)

            # New data to format
            additional_data = self._format_buffer_lines()
            all_data = existing_data_lines + additional_data
            delete_indices_from_list(self.indices_to_delete, all_data)

            theStr = self._format_header_info_lines()
            theStr += '\t"{}": \n{}'.format(ListDataStruct._DATA_STR, indentParagraph(self._format_data_list(all_data), 3))
            theStr += self._format_tail_lines()
            f.write(theStr)

            # Reset
            self.initial_filename = filename
            self.data_buffer = list()
            self.indices_to_delete = list()
            self.number_of_elements_in_file = len(all_data)

    @staticmethod
    def _format_data_list(theList):
        theStr = '[\n'

        for line in theList[:-1]:
            if not line.endswith(","):
                line = line + ","
            theStr += line + "\n"
        theStr += theList[-1] + "\n]"
        return theStr

    def _format_buffer_lines(self):
        theList = list()
        for item in self.data_buffer:
            text = json.dumps(obj_to_json(item))
            if self.compress_save:
                text = re.sub("\s*\"__module__\" *: *(\"(.*?)\"(,|\s|)|\s*\{(.*?)\}(,|\s|))", '', text)
                text = re.sub("\s*\"__class__\" *: *(\"(.*?)\"(,|\s|)|\s*\{(.*?)\}(,|\s|))", '', text)
            theList.append(text)
        return theList

    @staticmethod
    def load(filename, theClass=None):
        """
        Load the file filename.

        :param filename: file to load
        :param theClass: optional. Can be used to fix unpickling errors.
        :return: self-like object
        """
        if filename:
            if not os.path.splitext(filename)[-1].lower():
                filename += ListDataStruct.get_extension()
            try:
                newStruct = Memory_efficient_ListDataStruct()
                with open(filename, 'r') as f:
                    theDict = json.load(f)
                newStruct.set_info(decode_str_json(theDict[ListDataStruct._INFO_STR]))
                newStruct.initial_filename = filename
                newStruct.number_of_elements_in_file = len(theDict[ListDataStruct._DATA_STR])
                newStruct.data_buffer = list()
                newStruct.indices_to_delete = list()
                try:
                    newStruct.json_module_tree = theDict[ListDataStruct._COMPRESS_SAVE_STR]
                except KeyError:
                    newStruct.compress_save = False
                return newStruct
            except OSError:
                printIfShown("Could not read file ! " + filename, SHOW_WARNING)
            except EOFError:
                printIfShown("File empty ! " + filename, SHOW_WARNING)
        else:
            printIfShown("INVALID COLLECTION FILENAME: " + filename, SHOW_WARNING)

    def _get_json_module_tree(self):
        if not self.json_module_tree and len(self.data_buffer):
            self.json_module_tree = json.dumps(get_json_module_tree_from_dict(obj_to_json(self.data_buffer[0])))

    def add_data(self, data_in, clone=True):
        new_data = copy.deepcopy(data_in) if clone else data_in
        self.data_buffer.append(new_data)

    def get_data_at_index(self, index):
        if not (0 <= index <= len(self.data_buffer) + self.number_of_elements_in_file):
            raise IndexError("Out of bounds")

        if index > self.number_of_elements_in_file-1:
            return self.data_buffer[index-self.number_of_elements_in_file-1]
        else:
            # Find corresponding json item in file
            with open(self.initial_filename, "r", encoding='utf-8') as f:
                numberLinesBeforeData = self._format_header_info_lines().count("\n") + 2
                item = None
                for i, line in enumerate(f):
                    if numberLinesBeforeData + index == i:
                        item = line.strip()
                        break
            if item is None:
                raise IndexError()

            # Format it properly
            if item.endswith(','):
                item = item[:-1]
            # convert item to dictionary
            item = json.loads(item)
            # Uncompress it
            if self.compress_save:
                ListDataStruct._recursive_apply_moduleTree(json.loads(self.json_module_tree), item)
            return json_to_obj(item)

    def reset_data(self):
        self.initial_filename = None
        self.number_of_elements_in_file = 0
        self.data_buffer = list()
        self.indices_to_delete = list()

    def delete_points_at_indices(self, indices):
        self.indices_to_delete.extend(indices)

    def get_data(self):
        raise NotImplementedError("Invalid function for such data struct. Use generator or at_index instead")

    def merge(self, collection):
        raise NotImplementedError("Invalid function for such data struct.")


theLock = Lock()


class Performance_ListDataStruct(ListDataStruct_Interface):
    _INFO_STR = "info"
    _NBR_ELEMENTS = "nbr_elements"
    _STACK_SIZE = "stack_size"
    _COMPRESS_SAVE_STR = "module_tree"

    def __init__(self, stack_size=500):
        """
        This class is an extension to the classical :class:`ListDataStruct`.
        It is designed to be well suited to opimization: split huge files into smaller ones, efficient CPU usage, efficient RAM usage.

        :param stack_size: Number of elements to store on each file
        """
        super().__init__()
        self.compress_save = True
        self.data_buffer = list()
        self.curr_elements_in_last_file = 0
        self.curr_number_of_files = 1
        self.has_been_initialized = False
        self.stack_size = stack_size
        self.json_module_tree = ''
        self._mainfilename = ''

    def initialize(self, filename):
        rmtree(self._get_subfolder_path(filename), ignore_errors=True)
        os.makedirs(self._get_subfolder_path(filename))
        self._mainfilename = filename
        self.has_been_initialized = True

    @staticmethod
    def _get_subfolder_path(main_filename):
        folder_main = os.path.dirname(main_filename)
        filename = os.path.basename(main_filename)
        sub_folder, _ = os.path.splitext(filename)
        sub_folder += '_datafiles'
        return os.path.join(folder_main, sub_folder)

    @staticmethod
    def _get_current_data_filename(main_filename, curr_number_of_files):
        return os.path.join(Performance_ListDataStruct._get_subfolder_path(main_filename), "data_{}".format(curr_number_of_files))

    @staticmethod
    def split_list(numb_in_list, stack_size, thing_to_hash):
        # Returns [index_begin, index_end, lefts] to hash
        item_put_in_list = stack_size - numb_in_list
        item_still_to_be_put = len(thing_to_hash)
        max_number_to_put_in_list = min(item_still_to_be_put, item_put_in_list)
        hashed = [(0, max_number_to_put_in_list, numb_in_list + max_number_to_put_in_list)]
        if len(thing_to_hash) > item_put_in_list:
            returned_list = Performance_ListDataStruct.split_list(0, stack_size, thing_to_hash[item_put_in_list:])
            for k, item in enumerate(returned_list):
                index_begin_next, index_end_next, max_number_to_put_in_list = item
                mapped_index_begin = index_begin_next + item_put_in_list
                mapped_index_end = index_end_next + item_put_in_list
                returned_list[k] = (mapped_index_begin, mapped_index_end, max_number_to_put_in_list)
            hashed.extend(returned_list)
            return hashed
        return hashed

    def save(self, filename):
        global theLock
        with theLock:
            if not len(self.data_buffer):
                return

            if not self.has_been_initialized:
                self.initialize(filename)

            # Hash data to write
            splitlists = self.split_list(self.curr_elements_in_last_file, self.stack_size, self.data_buffer)
            for index_begin, index_end, numberofelem in splitlists:
                data_to_write = self.data_buffer[index_begin:index_end]
                self.curr_elements_in_last_file = numberofelem
                if data_to_write:
                    theStr = '\n'.join(data_to_write)
                    if os.path.exists(self._get_current_data_filename(filename, self.curr_number_of_files-1)):
                        theStr = "\n" + theStr
                    with open(self._get_current_data_filename(filename, self.curr_number_of_files-1), 'a+') as f:
                        f.write(theStr)

                # Increment number of elements or files
                if numberofelem == self.stack_size:
                    self.curr_number_of_files += 1
                    self.curr_elements_in_last_file = 0
                else:
                    self.curr_elements_in_last_file = numberofelem

            #  Write main file
            with open(filename, "w") as f:
                f.write(self._get_str_mainfile())
            self.data_buffer = list()

    def _get_str_mainfile(self):
        theDict = {self._INFO_STR: "{}".format(encode_str_json(self.get_info())),
                   self._NBR_ELEMENTS: self.get_total_nbr_elements(False),
                   self._STACK_SIZE: self.stack_size,
                   self._COMPRESS_SAVE_STR: self.json_module_tree}
        return json.dumps(theDict, indent=4)

    def get_total_nbr_elements(self, count_unsaved=True):
        nbr_elements_full_files = max(0, self.stack_size * (self.curr_number_of_files-1))
        nbr_elements_last_file = self.curr_elements_in_last_file
        unsaved_elements = len(self.data_buffer) if count_unsaved else 0
        return nbr_elements_full_files + nbr_elements_last_file + unsaved_elements

    def add_data(self, theData):
        theDict = obj_to_json(theData)
        theStr = json.dumps(theDict)
        if self.compress_save:
            theStr = re.sub("\s*\"__module__\" *: *(\"(.*?)\"(,|\s|)|\s*\{(.*?)\}(,|\s|))", '', theStr)
            theStr = re.sub("\s*\"__class__\" *: *(\"(.*?)\"(,|\s|)|\s*\{(.*?)\}(,|\s|))", '', theStr)
            self.save_moduletree(theDict)
        global theLock
        with theLock:
            self.data_buffer.append(theStr)

    def save_moduletree(self, theDict):
        if not self.json_module_tree:
            self.json_module_tree = json.dumps(get_json_module_tree_from_dict(theDict))

    def get_data_at_index(self, index):
        json_str = ''
        if self.get_total_nbr_elements(count_unsaved=True) < index:
            raise IndexError
        elif index >= self.get_total_nbr_elements(count_unsaved=False):  # data in buffer
            json_str = self.data_buffer[index-self.get_total_nbr_elements(count_unsaved=False)]
        else:  # data in files
            filenumber = int(floor(index/self.stack_size))
            linenumber = index - filenumber*self.stack_size
            with open(self._get_current_data_filename(self._mainfilename, filenumber), 'r') as f:
                for k, line in enumerate(f):
                    if k == linenumber:
                        json_str = line.strip()
                        break

        item = json.loads(json_str)
        ListDataStruct._recursive_apply_moduleTree(json.loads(self.json_module_tree), item)
        return json_to_obj(item)

    @staticmethod
    def load(filename, **kwargs):
        with open(filename, 'r', encoding="utf-8") as f:
            theDict = json.load(f)
        newStruct = Performance_ListDataStruct()
        try:
            newStruct.stack_size = theDict[Performance_ListDataStruct._STACK_SIZE]
        except KeyError:  # If it fails, it is probably a ListDataStruct
            return ListDataStruct.load(filename)
        newStruct.stack_size = theDict[Performance_ListDataStruct._STACK_SIZE]

        nbr_elements = theDict[Performance_ListDataStruct._NBR_ELEMENTS]
        number_of_files = int(floor(nbr_elements/newStruct.stack_size)) + 1
        number_of_elements_last_file = nbr_elements - (number_of_files-1)*newStruct.stack_size

        newStruct.stack_size = theDict[Performance_ListDataStruct._STACK_SIZE]
        newStruct.curr_elements_in_last_file = number_of_elements_last_file
        newStruct.curr_number_of_files = number_of_files
        newStruct.has_been_initialized = True
        newStruct.json_module_tree = theDict[Performance_ListDataStruct._COMPRESS_SAVE_STR]
        newStruct._mainfilename = filename
        return newStruct

    @staticmethod
    def load_as_listdatastruct(filename, **kwargs):
        """Return :class:`ListDataStruct`. Two-steps:
        1) Save temporary file formated like ListDataStruct
        2) Use ListDataStruct load function"""
        # 1)
        with open(filename, 'r', encoding="utf-8", newline='\n') as f:
            theDict = json.load(f)

        stack_size = theDict[Performance_ListDataStruct._STACK_SIZE]
        nbr_elements = theDict[Performance_ListDataStruct._NBR_ELEMENTS]
        number_of_files = int(floor(nbr_elements/stack_size)) + 1
        lines = list()
        for file_number in range(number_of_files):
            with open(Performance_ListDataStruct._get_current_data_filename(filename, file_number), 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.rstrip()
                    if not line:
                        continue
                    if line.isprintable():
                        lines.append(line)
                    else:
                        printIfShown("Removed line {}".format(line), SHOW_WARNING)
                # lines += list(filter(None, (line.rstrip() for line in f)))  # Non-blank lines
            printIfShown("loaded {} %".format(int(file_number/number_of_files*100)), SHOW_INFO)
        theStr = ''
        theStr += '{\n'
        #  noinspection PyProtectedMember
        theStr += '\t"{}": "{}",'.format(ListDataStruct._INFO_STR, theDict[Performance_ListDataStruct._INFO_STR])
        #  noinspection PyProtectedMember
        theStr += '\t"{}": {},'.format(ListDataStruct._COMPRESS_SAVE_STR, theDict[Performance_ListDataStruct._COMPRESS_SAVE_STR])
        #  noinspection PyProtectedMember
        theStr += '\t"{}": [\n{}\n]'.format(ListDataStruct._DATA_STR, "\n,".join(lines))
        theStr += '}'
        tempfile = filename + "_temp"
        with open(tempfile, "w", encoding="utf-8") as f:
            f.write(theStr)
        # 2)
        theDataStruct = ListDataStruct.load(tempfile, **kwargs)
        os.remove(tempfile)
        printIfShown("Done loading", SHOW_INFO)
        return theDataStruct

    def get_data_generator(self):
        """Get a generator to all the data stored"""
        for k in range(self.get_total_nbr_elements(count_unsaved=True)):
            yield self.get_data_at_index(k)
