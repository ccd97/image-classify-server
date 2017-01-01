import io
import os

import tensorflow as tf
from PIL import Image
from django.core.files.temp import NamedTemporaryFile
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

TF_GRAPH = "{base_path}/TF/graph.pb".format(
    base_path=os.path.abspath(os.path.dirname(__file__))
)

TF_LABELS = "{base_path}/TF/labels.txt".format(
    base_path=os.path.abspath(os.path.dirname(__file__))
)

sess = tf.Session()

with tf.gfile.FastGFile(TF_GRAPH, 'rb') as tf_graph:
    graph_def = tf.GraphDef()
    graph_def.ParseFromString(tf_graph.read())
    _ = tf.import_graph_def(graph_def, name='')
label_lines = [line.rstrip() for line in tf.gfile.GFile(TF_LABELS)]

softmax_tensor = sess.graph.get_tensor_by_name('final_result:0')


@csrf_exempt
def classify(request):
    data = {"success": False}

    if request.method == "POST":
        if request.FILES.get("image", None) is not None:
            image_request = request.FILES["image"]
            image_bytes = image_request.read()
            image = Image.open(io.BytesIO(image_bytes))
            tmp_file = NamedTemporaryFile()
            image.save(tmp_file, image.format)
            classify_result = tf_classify(tmp_file)

            if classify_result:
                data.update({"success": True})
                for res in classify_result:
                    data[res[0]] = '{:f}'.format(res[1])

    return JsonResponse(data)


# noinspection PyUnresolvedReferences
def tf_classify(image_file):
    result = list()

    image_data = tf.gfile.FastGFile(image_file.name, 'rb').read()

    predictions = sess.run(softmax_tensor, {'DecodeJpeg/contents:0': image_data})
    top_k = predictions[0].argsort()[-len(predictions[0]):][::-1]
    for node_id in top_k:
        human_string = label_lines[node_id]
        score = predictions[0][node_id]
        result.append([human_string, score])

    return result
