import os
import cv2
import numpy as np


# 特徴量としてパッチの平均RGBYを計算する
def calculate_features(img):
    r = img[:, :, 2].mean()
    g = img[:, :, 1].mean()
    b = img[:, :, 0].mean()
    y = 0.299 * r + 0.587 * g + 0.114 * b
    return np.array([r, g, b, y])


def create_mosaic_art(
    f_root = "./", 
    output_filename = "output.png",  # 上書き注意
    tgt_filename = "target.png",  
    f_candimgs = "cand_images/",  
    candimg_size = (50, 50),  # candimgのサイズ 
    tile_num = (100, 100),  # candimgを並べる数 
    e_greedy = 0.3,  # 最も類似している画像以外を選ぶ確率
    margin_gain = 2  # どれほど似ていない画像を許容するか
):

    # 素材の読み込み
    print("loading resources...")
    if not os.path.isfile(f_root + tgt_filename):
        print(f"{f_root + tgt_filename} is not found...")
        return False, None
    tgt = cv2.imread(f_root + tgt_filename, 1)

    candimgs = []
    candfeats = []
    candimgs_filenames = [f for f in os.listdir(f_root + f_candimgs) if '.png' in f or '.jpg' in f or '.bmp' in f]
    for file in candimgs_filenames:
        if not os.path.isfile(f_root + f_candimgs + file):
            print(f"{f_root + f_candimgs + file} is not found...")
            return False, None
        img = cv2.imread(f_root + f_candimgs + file, 1)
        ## 単純なresize
        # img = cv2.resize(img, candimg_size)  
        ## 真ん中をクリッピング
        h, w = img.shape[:2]
        xgain = w / candimg_size[0]
        ygain = h / candimg_size[1]
        if ygain < xgain:
            w1 = (int)(ygain * candimg_size[0] + 0.1)
            x1 = (int)((w - w1) / 2)
            img = img[:, x1:x1+w1, :]
        elif xgain < ygain:
            h1 = (int)(xgain * candimg_size[1] + 0.1)
            y1 = (int)((h - h1) / 2)
            img = img[y1:y1+h1, :]
        img = cv2.resize(img, candimg_size)  
        feat = calculate_features(img)
        candimgs.append(img)
        candfeats.append(feat)
    N = len(candimgs)
    candimgs = np.array(candimgs)
    candfeats = np.array(candfeats)

    # 出力する画像のサイズを計算する
    XDIV = candimg_size[0]
    YDIV = candimg_size[0]
    XNUM = tile_num[0]
    YNUM = tile_num[1]
    W = XDIV * XNUM
    H = YDIV * YNUM

    # 目標画像をリサイズして結果画像の下地として使う
    dst = cv2.resize(tgt, (W, H))

    # 目標画像の各パッチについて
    # 1. featuresを計算
    # 2. candfeatsの中で最も高いcandfeatのidを探す  #FIXME 確率で選ぶ？
    # 3. dstにcandimgs[id]を割り当てる
    # を繰り返す
    percent = 0
    for i in range(XNUM):
        for j in range(YNUM):
            p = (i * XNUM + j + 1) * 100 / (XNUM * YNUM)
            if p >= percent:
                print(f"Process : {percent}%")
                percent += 10
            x1 = i * XDIV
            x2 = x1 + XDIV
            y1 = j * YDIV
            y2 = y1 + YDIV
            patch = dst[y1:y2, x1:x2]
            # 1. tgt_featを計算
            tgt_feat = calculate_features(patch)
            # 2. tgt_featとcandfeatsを比較し最も類似しているidxを求める
            # e%で最適画像以外も選ぶようにする
            if np.random.rand() >= e_greedy:
                idx = np.sum(np.abs(candfeats - tgt_feat), 1).argmin()
            else:
                errors = np.sum(np.abs(candfeats - tgt_feat), 1)
                min_error = np.min(errors)
                while True:
                    idx = np.random.randint(0, N)
                    if min_error * margin_gain >= errors[idx]:
                        break
            dst[y1:y2, x1:x2] = (candimgs[idx])[:, :]

    # 結果画像の保存
    cv2.imwrite(f_root + output_filename, dst)
    return True, f_root + output_filename
    

if __name__ == "__main__":
    create_mosaic_art(
        f_root = "./", 
        output_filename = "output.png", 
        tgt_filename = "target.png", 
        f_candimgs = "cand_images/", 
        candimg_size = (8, 8), 
        tile_num = (70, 70), 
        e_greedy = 1.0,
        margin_gain = 1.2
    )
