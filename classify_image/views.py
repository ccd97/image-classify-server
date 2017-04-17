import io
import os

import tensorflow as tf
from PIL import Image
from base64 import b64decode
from django.core.files.temp import NamedTemporaryFile
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

MAX_K = 10

TF_GRAPH = "{base_path}/inception_model/graph.pb".format(
    base_path=os.path.abspath(os.path.dirname(__file__)))
TF_LABELS = "{base_path}/inception_model/labels.txt".format(
    base_path=os.path.abspath(os.path.dirname(__file__)))


def load_graph():
    sess = tf.Session()
    with tf.gfile.FastGFile(TF_GRAPH, 'rb') as tf_graph:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(tf_graph.read())
        _ = tf.import_graph_def(graph_def, name='')
    label_lines = [line.rstrip() for line in tf.gfile.GFile(TF_LABELS)]
    softmax_tensor = sess.graph.get_tensor_by_name('softmax:0')
    return sess, softmax_tensor, label_lines


SESS, GRAPH_TENSOR, LABELS = load_graph()


@csrf_exempt
def classify_api(request):
    data = {"success": False}

    if request.method == "POST":
        tmp_f = NamedTemporaryFile()

        if request.FILES.get("image", None) is not None:
            image_request = request.FILES["image"]
            image_bytes = image_request.read()
            image = Image.open(io.BytesIO(image_bytes))
            image.save(tmp_f, image.format)
        elif request.POST.get("image64", None) is not None:
            base64_data = request.POST.get("image64", None).split(',', 1)[1]
            plain_data = b64decode(base64_data)
            tmp_f.write(plain_data)

        classify_result = tf_classify(tmp_f, int(request.POST.get('k', MAX_K)))
        tmp_f.close()

        if classify_result:
            data.update({"success": True})
            for res in classify_result:
                data[res[0]] = '{:f}'.format(res[1])

    return JsonResponse(data)


def classify(request):
    return render(request, 'classify.html', {})


# noinspection PyUnresolvedReferences
def tf_classify(image_file, k=MAX_K):
    result = list()

    image_data = tf.gfile.FastGFile(image_file.name, 'rb').read()

    predictions = SESS.run(GRAPH_TENSOR, {'DecodeJpeg/contents:0': image_data})
    predictions = predictions[0][:len(LABELS)]
    top_k = predictions.argsort()[-k:][::-1]
    for node_id in top_k:
        label_string = LABELS[node_id]
        score = predictions[node_id]
        result.append([label_string, score])

    return result
