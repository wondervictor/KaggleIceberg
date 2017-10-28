# -*- coding: utf-8 -*-

import torch
from torch.autograd import Variable
import torch.optim as optimizer

import random
from model import cnn
from data import data_process as dp
import evaluation


def train(batch_size, epoches):

    train_data, test_data = dp.load_train_data('data')

    model = cnn.CNNet()

    num_samples = len(train_data)

    learning_rate = 0.0001

    criterion = torch.nn.CrossEntropyLoss()
    train_optimizer = optimizer.RMSprop(params=model.parameters(), lr=learning_rate)

    for i in range(epoches):
        print("Epoch: %s:" % (i + 1))
        random.shuffle(train_data)
        sum_loss = 0
        for j in range(num_samples/batch_size):

            images = []
            labels = []

            for sample_index in range(batch_size):
                images.append(train_data[sample_index+j][0])
                labels.append(train_data[sample_index+j][1])

            images = Variable(torch.FloatTensor(images))
            labels = Variable(torch.LongTensor(labels))

            prob = model(images)
            loss = criterion(prob, labels)
            sum_loss += loss.data.numpy()[0]
            train_optimizer.zero_grad()
            loss.backward()
            train_optimizer.step()

            if j % 5 == 0:
                print("Batch Index: %s Loss: %s Avg Loss: %s" % (j, loss.data.numpy()[0], sum_loss/(j+1)))

        print("Epoch: %s Loss: %s" % (i, sum_loss/(num_samples/batch_size)))

        torch.save(model, 'model_params/epoch_%s_params' % i)
        labels, result = test(test_data, model)
        acc = evaluation.evaluation(result, labels)
        with open('test.log', 'w+') as f:
            f.write("TEST: %s ACC: %s\n" % (i, acc))


def test(dataset, model):

    if isinstance(model, str):
        model = torch.load(model)

    num_samples = len(dataset)

    labels = []
    result = []
    for i in range(num_samples):
        image = dataset[i][0]
        labels.append(dataset[i][1])

        image = Variable(torch.FloatTensor(image))
        image = image.unsqueeze(0)
        prob = model(image)

        prob = prob.squeeze(0)
        prob = prob.data.numpy()
        result.append(prob)

    return labels, result


def predict(x, model):

    image = Variable(torch.FloatTensor(x))
    image = image.unsqueeze(0)
    prob = model(image)

    prob = prob.squeeze(0)
    prob = prob.data.numpy()

    return prob[1]


if __name__ == '__main__':

    train(16, 20)