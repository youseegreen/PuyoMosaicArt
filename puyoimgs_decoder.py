''' 
puyoimgs.pngを分割する
'''

import cv2

input_filename = "puyoimgs.png"  
subimg_width = 15
subimg_height = 15
subimgs_xnum = 40
subimgs_ynum = 20

f_output = "./cand_images/"  # 出力先

src = cv2.imread(input_filename, 1)
for i in range(subimgs_xnum):
    for j in range(subimgs_ynum):
        x1 = i * subimg_width
        x2 = x1 + subimg_width
        y1 = j * subimg_height
        y2 = y1 + subimg_height
        filename = "{}.png".format((str)(i * subimgs_ynum + j).zfill(5))
        cv2.imwrite(f_output + filename, src[y1:y2, x1:x2])
