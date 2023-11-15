# Medical_Image

### Results
- Results on patches
- Results on patients

<details close>
<summary><b>Performance Autoencoder approach:</b></summary>

![results1](/figure/seven_results.png)


</details>

<details close>
<summary><b>Performance CNN approach:</b></summary>

![results1](/figure/seven_results.png)


</details>


## 1. Create Environment

- Make Conda Environment
```
Ficar com crear el environment desde el yml
conda create -n x python=3.7
conda activate x
```

&nbsp;

## 2. Prepare Dataset
Download the following datasets:

LOL-v1 [Baidu Disk](https://pan.baidu.com/s/1ZAC9TWR-YeuLIkWs3L7z4g?pwd=cyh2) (code: `cyh2`), [Google Drive](https://drive.google.com/file/d/1L-kqSQyrmMueBh_ziWoPFhfsAh50h20H/view?usp=sharing)

&nbsp;                    


## 3. Testing

Download our models from [Baidu Disk](https://pan.baidu.com/s/13zNqyKuxvLBiQunIxG_VhQ?pwd=cyh2) (code: `cyh2`) or [Google Drive](https://drive.google.com/drive/folders/1ynK5hfQachzc8y96ZumhkPPDXzHJwaQV?usp=drive_link). Put them in folder `pretrained_weights`

```shell
# Autoencoder
python3 Enhancement/test_from_dataset.py --opt Options/RetinexFormer_LOL_v1.yml --weights pretrained_weights/LOL_v1.pth --dataset LOL_v1
```

```shell
# CNN
python3 Enhancement/test_from_dataset.py --opt Options/RetinexFormer_LOL_v2_real.yml --weights pretrained_weights/LOL_v2_real.pth --dataset LOL_v2_real
```

- Evaluating the Params and FLOPS of models


&nbsp;


## 4. Training

Feel free to check our training logs from [Baidu Disk](https://pan.baidu.com/s/16NtLba_ANe3Vzji-eZ1xAA?pwd=cyh2) (code: `cyh2`) or [Google Drive](https://drive.google.com/drive/folders/1HU_wEn_95Hakxi_ze-pS6Htikmml5MTA?usp=sharing)

```shell
# Autoencoder
python3 basicsr/train.py --opt Options/RetinexFormer_LOL_v1.yml
```

```shell
# CNN
python3 basicsr/train.py --opt Options/RetinexFormer_LOL_v2_real.yml
```
&nbsp;
