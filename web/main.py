import sys
import traceback
import json
import web

from sai import SaiObjType
from sai_npu import SaiNpu


# Initialize SAI
exec_params = {
    "server": "localhost",
    "traffic": False,
    "saivs": False,
    "loglevel": "NOTICE",
    "sku": None
}
sai = SaiNpu(exec_params)

# Url mappings
urls = ("/", "Dashboard",
        "/attributes/(\w+)/", "Attributes",
        "/objects/(\w+)/", "ObjectList",
        "/objects/(\w+)/oid:(\w+)/", "Object",
        "/data/objects/(\w+)/", "DataObjectList",
        "/data/objects/(\w+)/oid:(\w})/", "DataObject",)

# Fill in SAI attributes
attributes = {}

try:
    f = open('config.json')
    attributes = json.load(f) # sorted(json.load(f), key=lambda x: x['name'])
    f.close()
except OSError:
    exit()


# Templates
t_globals = {'attributes': attributes}
render = web.template.render("templates", base="base", globals=t_globals)


class Dashboard:
    def GET(self):
        title = "Dashboard"

        # oids = sai.get_oids()
        return render.dashboard(title, attrs=t_globals["attributes"])


class Object:
    def GET(self, name, oid):
        title = "SAI Objects - {0}".format(name)
        oid = 'oid:' + oid
        objects = [oid]
        objects.insert(0, 'name')
        return render.objects(title, name, fields=objects, attrs=t_globals["attributes"])


class ObjectList:
    def GET(self, name):
        title = "SAI Objects - {0}".format(name)
        short_name = name.replace('SAI_OBJECT_TYPE_', '')
        objects = sai.get_oids(SaiObjType[short_name])[short_name]
        objects.insert(0, 'name')
        return render.objects(title, name, fields=objects, attrs=t_globals["attributes"])


class DataObjectList:
    def GET(self, name):
        short_name = name.replace('SAI_OBJECT_TYPE_', '')
        objects = sai.get_oids(SaiObjType[short_name])[short_name]
        attribs = [z for z in attributes if z['name'] == name][0]['attributes']

        rows = []
        for idx in range(len(attribs)):
            attribute_name = attribs[idx]['name']

            # TODO: Need to map unsupported type to a generic one
            attribute_type = attribs[idx]['properties']['type']['genericType'] if 'genericType' in attribs[
                idx]['properties']['type']['genericType'] else attribs[idx]['properties']['type']
            attribute_objs = attribs[idx]['properties']['objects'] if 'objects' in attribs[idx]['properties'].keys(
            ) else 'N/A'

            row = {'name': attribute_name,
                   'type': attribute_type, 'objs': attribute_objs}
            for idx2 in range(len(objects)):
                object = objects[idx2]

                print('TYPE: {0}'.format(attribute_type))

                err, val = sai.get_by_type(
                    object, attribute_name, attribute_type, False)
                val = json.loads(val.data)[
                    1] if err == 'SAI_STATUS_SUCCESS' else err
                row[object] = val
            rows.append(row)

        return json.dumps(rows)


class DataObjectList:
    def GET(self, name):

        short_name = name.replace('SAI_OBJECT_TYPE_', '')
        objects = sai.get_oids(SaiObjType[short_name])[short_name]
        attribs = [z for z in attributes if z['name'] == name][0]['attributes']

        rows = []
        for idx in range(len(attribs)):
            attribute_name = attribs[idx]['name']

            # TODO: Need to map unsupported type to a generic one
            attribute_type = attribs[idx]['properties']['genericType'] if 'genericType' in attribs[idx]['properties'].keys(
            ) else attribs[idx]['properties']['type']
            attribute_objs = attribs[idx]['properties']['objects'] if 'objects' in attribs[idx]['properties'].keys(
            ) else 'N/A'

            fetchError = False
            row = {'name': attribute_name,
                   'type': attribute_type,
                   'objs': attribute_objs}
                   
            for idx2 in range(len(objects)):
                object = objects[idx2]

                try:
                    err, val = sai.get_by_type(
                        object, attribute_name, attribute_type, False)
                    val = json.loads(val.data)[
                        1] if err == 'SAI_STATUS_SUCCESS' else err
                except AssertionError:
                    # TODO: uncomment to get more details on assert()
                    # _, _, tb = sys.exc_info()
                    # traceback.print_tb(tb) # Fixed format
                    # val = 'SYS_UNREACHABLE'
                    fetchError = True
                    print("ATTRIBUTE\t'{0} with type {1} fetch failed".format(attribute_name, attribute_type), file=sys.stderr, flush=True)
                    break

                row[object] = val
            if not fetchError:
                rows.append(row)
            else:
                break

        return json.dumps(rows)


class Attributes:
    def GET(self, name):
        title = "SAI Attributes - {0}".format(name)
        attribute = [z for z in attributes if z['name'] == name][0]
        return render.attributes(title, attribute, attrs=t_globals["attributes"])


app = web.application(urls, globals())

if __name__ == "__main__":
    app.run()
