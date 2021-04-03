from collections import OrderedDict




class AudioFeature(OrderedDict):
    """
    Basically is a dictionar whose keys will be the name of the feature, and the value will be the features values.

    The AudioFeature is an OrderedDict, this is, remembers the order in which the elements have been inserted.
    This is useful for MAAP.AudioFeatureExtractor. AudiFeatureExtractor analyses a signal and computes its feactures,
    and returns them as output, using this class instance. It is desired that, for different sets of features selected in
    AudioFeatureExtractor, the organization of the output is well organized, i.e, their items are sorted. As example,
    a sort strategy could be sort the keys alphabetically. The OrderedDict inheritance allows AudioFeatureExtractor
    to control how features are organized in AudioFeature instance. For that, AudiFeatureExtractor will need to
    insert the features with the desired order, in order to AudioFeature remember it.


    TOIMPROVE: Currently, the AudioFeature allows its good organization because inherits a OrderedDict. Its organization
         depends how their keys are inserted. For now, this process is managed by how calls AudioFeature instance.
         In the future, should be AudioFeature to manage that internally

    """

    def __init__(self,):
        """Constructor for AudioFeature"""
        super().__init__()

    def __repr__(self):
        class_name = type(self).__name__
        features = list(self.keys())
        return '{}(features={})'.format(class_name, features)

    '''
    Setters/Loaders
    '''

    '''
    Getters
    '''

    '''
    Workers
    '''

    '''
    Logic methods 
    '''

    '''
    Checkers
    '''

    '''
    Util methods / Static methods 
    '''


