import axios, { CancelToken } from "axios";
import { getFullUrl } from "utils";

const http = axios.create({
  // baseURL: "/",
  headers: {
    "Content-type": "application/json",
  },
});

class UploadFilesService {
  cancel: any;

  constructor() {
    //@ts-ignore
    this.cancel = null;
  }

  upload(
    url: string,
    data: Object,
    onUploadProgress: (progressEvent: any) => void,
    token: string
  ) {
    let formData = new FormData();

    Object.keys(data).forEach((k) => {
      // @ts-ignore
      formData.append(k, data[k]);
    });

    return http.post(getFullUrl(url) || getFullUrl("/api/upload/"), formData, {
      // @ts-ignore
      cancelToken: new CancelToken((c) => {
        this.cancel = c;
      }),
      headers: {
        "Content-Type": "multipart/form-data",
        Authorization: `Bearer ${token}`,
      },
      onUploadProgress,
    });
  }

  cancelRequest() {
    // @ts-ignore
    this.cancel();
  }

  getFiles() {
    return http.get("/files");
  }
}

export default new UploadFilesService();
