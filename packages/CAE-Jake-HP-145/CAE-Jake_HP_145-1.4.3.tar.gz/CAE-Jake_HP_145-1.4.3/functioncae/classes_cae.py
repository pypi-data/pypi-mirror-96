"""docstring"""


import keras
import numpy as np
from skimage.io import imread
from skimage.transform import resize
from sklearn.utils import shuffle


class MassesSequence(keras.utils.Sequence):
    """ Classe per fare data augmentation per CAE """

    def __init__(  # pylint: disable=R0913
        self, images, masks, label_array, img_gen, batch_size=10, shape=(124, 124)
    ):
        """

        :type images: np.array
        :param images: immagini

        :type masks: np.array
        :param masks: maschere

        :type label_array: np.array
        :param label_array: label di classificazione (benigno o maligno)

        :type batch_size: int
        :param batch_size: dimensione della batch

        :type img_en: ImageDatagenerator
        :param img_gen: istanza della classe ImageDatagenerator

        :type shape: tuple
        :type shape: dimensione delle immagini. Di default (124, 124)

        """
        self.images, self.masks, self.label_array = images, masks, label_array
        self.shape = shape
        self.img_gen = img_gen
        self.batch_size = batch_size

    def __len__(self):
        """restituisce il rapporto tra la lunghezza del vettore delle immagini
        e la dimensione della batch
        """
        return len(self.images) // self.batch_size

    def on_epoch_end(self):
        """Mischia il dataset a fine epoca."""
        self.images, self.masks, self.label_array = shuffle(
            self.images, self.masks, self.label_array
        )

    def process(self, img, transform):
        """ Applica una trasformazione random all'immagine"""
        img = self.img_gen.apply_transform(img, transform)
        return img

    def __getitem__(self, idx):
        """Organizza le immagini,maschere e classi in batch"""
        batch_images = self.images[idx * self.batch_size : (idx + 1) * self.batch_size]
        batch_masks = self.masks[idx * self.batch_size : (idx + 1) * self.batch_size]
        batch_label_array = self.label_array[
            idx * self.batch_size : (idx + 1) * self.batch_size
        ]

        images_list = []
        masks_list = []
        classes_ = []

        for image, mask, label in zip(batch_images, batch_masks, batch_label_array):
            transform = self.img_gen.get_random_transform(self.shape)
            images_list.append(self.process(image, transform))
            masks_list.append(self.process(mask, transform) > 0.2)
            classes_.append(label)

        return np.asarray(images_list, np.float64), [
            np.asarray(masks_list, np.float64),
            np.asarray(classes_, np.float),
        ]


class MassesSequenceRadiomics(keras.utils.Sequence):
    """ Classe per il data augmentation per CAE con feature radiomiche """

    def __init__(  # pylint: disable=R0913
        self,
        images,
        masks,
        label_array,
        features,
        img_gen,
        batch_size=10,
        shape=(124, 124),
    ):
        """Inizializza la sequenza



        :type images: np.array
        :param images: immagini

        :type masks: np.array
        :param masks: maschere

        :type label_array: np.array
        :param label_array: label di classificazione (benigno o maligno)

        :type features: np.array
        :param features: feature ottenute con pyradiomics

        :type batch_size: int
        :param batch_size: dimensione della batch

        :type img_en: ImageDatagenerator
        :param img_gen: istanza della classe ImageDatagenerator

        :type shape: tuple
        :type shape: dimensione delle immagini. Di default (124, 124)


        """
        self.images, self.masks, self.label_array, self.features = (
            images,
            masks,
            label_array,
            features,
        )
        self.shape = shape
        self.img_gen = img_gen
        self.batch_size = batch_size

    def __len__(self):
        """restituisce il rapporto tra la lunghezza del vettore delle immagini
        e la dimensione della batch
        """
        return len(self.images) // self.batch_size

    def on_epoch_end(self):
        """Mischia il dataset a fine epoca."""
        self.images, self.masks, self.label_array, self.features = shuffle(
            self.images, self.masks, self.label_array, self.features
        )

    def process(self, img, transform):
        """ Applica una trasformazione random all'immagine"""
        img = self.img_gen.apply_transform(img, transform)
        return img

    def __getitem__(self, idx):
        """Organizza le immagini,maschere, classi e feature in batch"""

        batch_images = self.images[idx * self.batch_size : (idx + 1) * self.batch_size]
        batch_masks = self.masks[idx * self.batch_size : (idx + 1) * self.batch_size]
        batch_label_array = self.label_array[
            idx * self.batch_size : (idx + 1) * self.batch_size
        ]
        batch_features = self.features[
            idx * self.batch_size : (idx + 1) * self.batch_size
        ]

        images_list = []
        masks_list = []
        classes_ = []
        features_ = []

        for image, mask, label, feature in zip(
            batch_images, batch_masks, batch_label_array, batch_features
        ):
            transform = self.img_gen.get_random_transform(self.shape)
            images_list.append(self.process(image, transform))
            masks_list.append(self.process(mask, transform) > 0.2)
            classes_.append(label)
            features_.append(feature)

        return [
            np.asarray(images_list, np.float64),
            np.asarray(features_, np.float64),
        ], [
            np.asarray(masks_list, np.float64),
            np.asarray(classes_, np.float),
        ]


class MassesSequenceRadiomicsBig(keras.utils.Sequence):  # pylint: disable=R0902
    """ Classe per data augmentation per CAE con grande dataset """

    def __init__(  # pylint: disable=R0913
        self,
        images,
        masks,
        label_array,
        features,
        img_gen,
        batch_size=5,
        shape=(2048, 1536),
        shape_tensor=(2048, 1536, 1),
    ):
        """Inizializza la sequenza

        :type images: np.array
        :param images: path delle immagini

        :type masks: np.array
        :param masks: path delle maschere

        :type label_array: np.array
        :param label_array: label di classificazione (benigno o maligno)

        :type features: np.array
        :param features: feature ottenute con pyradiomics

        :type batch_size: int
        :param batch_size: dimensione della batch

        :type img_en: ImageDatagenerator
        :param img_gen: istanza della classe ImageDatagenerator

        :type shape: tuple
        :type shape: dimensione delle immagini. Di default (2048, 1536)

        :type shape_tensor: tuple
        :type shape_tensor: dimensione del tensore di reshape. Di default (2048,1536,1)

        """
        self.images, self.masks, self.label_array, self.features = (
            images,
            masks,
            label_array,
            features,
        )
        self.shape = shape
        self.shape_tensor = shape_tensor
        self.img_gen = img_gen
        self.batch_size = batch_size

    def __len__(self):
        """restituisce il rapporto tra la lunghezza del vettore delle immagini
        e la dimensione della batch
        """
        return len(self.images) // self.batch_size

    def on_epoch_end(self):
        """Mischia il dataset a fine epoca."""
        self.images, self.masks, self.label_array, self.features = shuffle(
            self.images, self.masks, self.label_array, self.features
        )

    def process(self, img, transform):
        """ Applica una trasformazione random all'immagine"""
        img = self.img_gen.apply_transform(img, transform)
        return img

    def __getitem__(self, idx):  # pylint: disable=R0914
        """Organizza le immagini,maschere, classi e feature in batch"""
        batch_images = self.images[idx * self.batch_size : (idx + 1) * self.batch_size]
        batch_masks = self.masks[idx * self.batch_size : (idx + 1) * self.batch_size]
        batch_label_array = self.label_array[
            idx * self.batch_size : (idx + 1) * self.batch_size
        ]
        batch_features = self.features[
            idx * self.batch_size : (idx + 1) * self.batch_size
        ]

        images_list = []
        masks_list = []
        classes_ = []
        features_ = []

        for image, mask, label, feature in zip(
            batch_images, batch_masks, batch_label_array, batch_features
        ):
            transform = self.img_gen.get_random_transform(self.shape)
            images_el = resize(imread(str(image)), self.shape_tensor)
            masks_el = resize(imread(str(mask)), self.shape_tensor)
            images_list.append(self.process(images_el, transform))
            del images_el
            masks_list.append(self.process(masks_el, transform))
            del masks_el
            classes_.append(label)
            features_.append(feature)

        return [np.array(images_list) / 255, np.asarray(features_, np.float64)], [
            np.array(masks_list) / 255,
            np.asarray(classes_, np.float),
        ]


class ValidatorGenerator(keras.utils.Sequence):
    """Classe per generare i dati di validazione in batch per il dataset grande"""

    def __init__(  # pylint: disable=R0913
        self,
        images,
        masks,
        label_array,
        features,
        batch_size=5,
        shape=(1024, 768),
        shape_tensor=(1024, 768, 1),
    ):
        """Inizializza la sequenza

        :type images: np.array
        :param images: path delle immagini

        :type masks: np.array
        :param masks: path delle maschere

        :type label_array: np.array
        :param label_array: label di classificazione (benigno o maligno)

        :type features: np.array
        :param features: feature ottenute con pyradiomics

        :type batch_size: int
        :param batch_size: dimensione della batch

        :type shape: tuple
        :type shape: dimensione delle immagini. Di default (2048, 1536)

        :type shape_tensor: tuple
        :type shape_tensor: dimensione del tensore di reshape. Di default (2048,1536,1)

        """
        self.images, self.masks, self.label_array, self.features = (
            images,
            masks,
            label_array,
            features,
        )
        self.shape = shape
        self.batch_size = batch_size
        self.shape_tensor = shape_tensor

    def __len__(self):
        """restituisce il rapporto tra la lunghezza del vettore delle immagini
        e la dimensione della batch
        """
        return len(self.images) // self.batch_size

    def __getitem__(self, idx):  # pylint: disable=R0914
        """Organizza le immagini,maschere, classi e feature di validazione in batch"""

        batch_images = self.images[idx * self.batch_size : (idx + 1) * self.batch_size]
        batch_masks = self.masks[idx * self.batch_size : (idx + 1) * self.batch_size]
        batch_label_array = self.label_array[
            idx * self.batch_size : (idx + 1) * self.batch_size
        ]
        batch_features = self.features[
            idx * self.batch_size : (idx + 1) * self.batch_size
        ]

        images_list = []
        masks_list = []
        classes_ = []
        features_ = []

        for image, mask, label, feature in zip(
            batch_images, batch_masks, batch_label_array, batch_features
        ):

            images_el = resize(imread(str(image)), self.shape_tensor)
            masks_el = resize(imread(str(mask)), self.shape_tensor)
            images_list.append(images_el)
            del images_el
            masks_list.append(masks_el)
            del masks_el
            classes_.append(label)
            features_.append(feature)

        return [np.array(images_list) / 255, np.asarray(features_, np.float64)], [
            np.array(masks_list) / 255,
            np.asarray(classes_, np.float),
        ]
