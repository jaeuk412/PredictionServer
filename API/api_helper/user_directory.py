# -*- coding: utf-8 -*-

root_path = '/home/uk/PredictionServer'
folder_path = root_path + '/prediction/prediction_ETRI/'
folder_path2 = root_path +'/prediction2/'
folder_path3 = root_path +'/API/DataSet/uploadfiles/'


## 개인 ProjectEn 경로 ##
own_path='/home/imr-ai/psycho_2_7/ProjectEn/'
# own_path='/home/etri/AI-Web/ProjectEn/'

# ip_path
ip_path='http://localhost'

# e_test_path
e_test_path='/home/imr-ai/psycho_2_7/ProjectEn/AAE/trained/aae-mfcc/epoch-1001-best/'

# Dataset, csv 파일 저장
my_dataset_path=own_path+'audio'
my_csvfile_path= own_path+'csvfile'

# Test Dataset 경로
test_dataset_path = own_path+'anomaly_check/sound'

# Dataset 전처리
result_save_path_dataset= own_path+'save_result/datasets/'

# Training, Test 폴더 저장.
result_save_path_project = own_path+'save_result/projects/'

# 실행파일 저장되 있는곳
backend_test_path = own_path+'backend_test/'

# 모델 visualization 저장 된 곳
model_visualization_save = own_path+'model_visualization/'

# GIP 3D 이미지 파일 저장 (고정)
result_3D_image = own_path+'AAE/test_result/latent_result'
cudaversion='/usr/local/cuda-9.0/version.txt'


# def dataset_path():
#     dataset_path= my_dataset_path
#     return dataset_path

def csvfile_path():
    csvfile_path= my_csvfile_path
    return csvfile_path

def model_visualization(model_id):

    if model_id == 1:
        filename = 'test-model.svg'
    else:
        filename = 'test-model-01000.svg'

    return filename


def dataset_result_path(dataset_id):
    dataset_path= result_save_path_dataset + 'dataset_'+ str(dataset_id)+'/'
    #'/home/etri/AI-Web/ProjectEn/saveHDF/1/'
    return dataset_path

# def project_result_path(project_id):
#     project_path= result_save_path_project + 'project_' + str(project_id) +'/'
#     #'/home/etri/AI-Web/ProjectEn/saveHDF/1/'
#     return project_path
#
# def job_result_path(project_id, job_id):
#     job_path= project_result_path(project_id) + 'job_' + str(job_id)+'/'
#     #'/home/etri/AI-Web/ProjectEn/saveHDF/1/1_training/'
#     return job_path

# def training_result_path(project_id, job_id, train_id):
#     training_path= job_result_path(project_id, job_id) + 'train_' + str(train_id)+'/'
#     #'/home/etri/AI-Web/ProjectEn/saveHDF/1/1_training/'
#     return training_path
#
# def test_result_path(project_id, job_id, train_id, test_id):
#     test_path= training_result_path(project_id, job_id, train_id) + 'test_' + str(test_id)+'/'
#     #'/home/etri/AI-Web/ProjectEn/saveHDF/1/1_training/1'
#     return test_path

def training_result_path(project_id, job_id, train_id):
    training_path= result_save_path_project + 'train_' + str(train_id)+'/'
    #'/home/etri/AI-Web/ProjectEn/saveHDF/1/1_training/'
    return training_path

def test_result_path(project_id, job_id, train_id, test_id):
    test_path= result_save_path_project + 'test_' + str(test_id)+'/'
    #'/home/etri/AI-Web/ProjectEn/saveHDF/1/1_training/1'
    return test_path

# def training_result_path(dataset_id,model_id,training_name):
#     training_path= result_save_path + str(dataset_id) +'/'+ str(model_id)+'_'+str(training_name)+'/'
#     #'/home/etri/AI-Web/ProjectEn/saveHDF/1/1_training/'
#     return training_path

# def test_result_path(dataset_id,model_id,training_name,test_id):
#     test_path= result_save_path + str(dataset_id) +'/'+ str(model_id)+'_'+str(training_name)+'/'+str(test_id)+'/'
#     #'/home/etri/AI-Web/ProjectEn/saveHDF/1/1_training/1'
#     return test_path




# print(dataset_result_path(1))
# print(training_result_path(1,1,'gogo'))
# print(test_result_path(1,1,32,5))