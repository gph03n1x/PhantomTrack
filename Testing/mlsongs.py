from sklearn import tree
from numpy import array
from scipy.io.wavfile import read

samples = 1024*10
print(samples)
input_data_1 = read("Ludvig Forssell - A Phantom Pain [lyric video]-wlp8GimssgI.wav")
audio_1 = [i for i in input_data_1[1]]
audio_1 = audio_1[::int(len(audio_1)/samples)][:samples]


input_data_2 = read("Metal Gear Rising - Revengeance OST - I'm My Own Master Now Extended-6RlSgnpLbro.wav")
audio_2 =[i for i in input_data_2[1]]
audio_2 = audio_2[::int(len(audio_2)/samples)][:samples]

input_data_3 = read("Kindred, the Eternal Hunters _ Login Screen - League of Legends-aB_DbCpFvHA.wav")
audio_3 = [i for i in input_data_3[1]]
audio_3 = audio_3[::int(len(audio_3)/samples)][:samples]

input_data_4 = read("GW2 - Heart of Thorns Soundtrack - 'Main Theme'-QtvnP91PDfQ.wav")
audio_4 = [i for i in input_data_4[1]]
audio_4 = audio_4[::int(len(audio_4)/samples)][:samples]

input_data_5 = read("Major Lazer & DJ Snake - Lean On (feat. MØ) (Official Music Video)-YqeW9_5kURI.wav")
audio_5 = [i for i in input_data_5[1]]
audio_5 = audio_5[::int(len(audio_5)/samples)][:samples]

input_data_6 = read("Coldplay - Hymn For The Weekend (Official Video)-YykjpeuMNEk.wav")
audio_6 = [i for i in input_data_6[1]]
audio_6 = audio_6[::int(len(audio_6)/samples)][:samples]
print(len(audio_1), len(audio_2))



features = [
    [*audio_1,*audio_2],
    [*audio_3,*audio_4]
]
print(features[:1024])
labels = [1, 0]

clf = tree.DecisionTreeClassifier()
clf = clf.fit(features, labels)
print(clf.predict([*audio_5,*audio_6]))