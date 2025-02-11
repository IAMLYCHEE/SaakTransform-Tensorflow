import torch
import codecs



def parse_byte(b):
    if isinstance(b, str):
        return ord(b)
    return b


def get_int(b):
    return int(codecs.encode(b, 'hex'), 16)

def read_image_file(path):
    with open(path, 'rb') as f:
        data = f.read()
        assert get_int(data[:4]) == 2051
        length = get_int(data[4:8])
        num_rows = get_int(data[8:12])
        num_cols = get_int(data[12:16])
        images = []
        idx = 16
        for l in range(length):
            img = []
            images.append(img)
            for r in range(num_rows):
                row = []
                img.append(row)
                for c in range(num_cols):
                    row.append(parse_byte(data[idx]))
                    idx += 1
        assert len(images) == length
        return torch.ByteTensor(images).view(-1, 28, 28)



def read_label_file(path):
    with open(path, 'rb') as f:
        data = f.read()
        assert get_int(data[:4]) == 2049
        length = get_int(data[4:8])
        labels = [parse_byte(b) for b in data[8:]]
        assert len(labels) == length
        return torch.LongTensor(labels)










# from utils import read_image_file, read_label_file
import os
import torch.utils.data as data
# import torch
from PIL import Image


class MNIST(data.Dataset):
    raw_folder = 'raw'
    processed_folder = 'processed'
    training_file = 'training.pt'
    test_file = 'test.pt'


    def __init__(self,root='./data',train=True,transform=None,target_transform=None,process=False):
        self.transform=transform
        self.target_transform=target_transform
        self.train=train
        self.root=root

        if process:
            self.process()


        if not self._check_exists():
            raise RuntimeError('Dataset not fpound')

        if self.train:
            self.train_data,self.train_label=torch.load(
                os.path.join(self.root,self.processed_folder,self.training_file)
            )
        else:
            self.test_data,self.test_label=torch.load(
                os.path.join(self.root,self.processed_folder,self.test_file)
            )



    def __getitem__(self,index):

        if self.train:
            img,target=self.train_data[index],self.train_label[index]
        else:
            img,target=self.test_data[index],self.test_label[index]

        img=Image.fromarray(img.numpy(),mode='L')

        if self.transform is not None:
            img=self.transform(img)

        if self.target_transform is not None:
            target=self.target_transform(target)

        return img,target


    def __len__(self):
        if self.train:
            return len(self.train_data)
        else:
            return len(self.test_data)



    def _check_exists(self):
        return os.path.exists(os.path.join(self.root,self.processed_folder,self.training_file)) and \
               os.path.exists(os.path.join(self.root,self.processed_folder,self.test_file))


    def process(self):
        import gzip

        try:
            os.makedirs(os.path.join(self.root,self.raw_folder))
            os.makedirs(os.path.join(self.root,self.processed_folder))
        except:
            pass


        files=os.listdir(self.raw_folder)

        for file in files:
            print('Processing %s' % file)
            file_path=os.path.join(self.root,self.raw_folder,file)
            with open(file_path.replace('.gz',''),'wb') as out_f, \
                gzip.GzipFile(file_path) as zip_f:
                out_f.write(zip_f.read())


        training_set = (
            read_image_file(os.path.join(self.root, self.raw_folder, 'train-images-idx3-ubyte')),
            read_label_file(os.path.join(self.root, self.raw_folder, 'train-labels-idx1-ubyte'))
        )
        test_set = (
            read_image_file(os.path.join(self.root, self.raw_folder, 't10k-images-idx3-ubyte')),
            read_label_file(os.path.join(self.root, self.raw_folder, 't10k-labels-idx1-ubyte'))
        )
        with open(os.path.join(self.root, self.processed_folder, self.training_file), 'wb') as f:
            torch.save(training_set, f)
        with open(os.path.join(self.root, self.processed_folder, self.test_file), 'wb') as f:
            torch.save(test_set, f)

        print('Done!')


if __name__=='__main__':
    mnist_train=MNIST(train=True,process=False)
    print (len(mnist_train))