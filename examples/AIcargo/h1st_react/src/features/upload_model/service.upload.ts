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
    token?: string
  ) {
    let formData = new FormData();

    Object.keys(data).forEach((k) => {
      // @ts-ignore
      formData.append(k, data[k]);
    });

    const headers = {
      "Content-Type": "multipart/form-data",
    };

    if (token) {
      // @ts-ignore
      headers.Authorization = `Bearer ${token}`;
    }

    // TODO fix this to enable pathname segment
    return http.post(url || getFullUrl("/api/upload/"), formData, {
      // @ts-ignore
      cancelToken: new CancelToken((c) => {
        this.cancel = c;
      }),
      headers,
      onUploadProgress,
    });
  }

  cancelRequest() {
    // @ts-ignore
    if (typeof this.cancel === "function") {
      this.cancel();
    }
  }

  getFiles() {
    return http.get("/files");
  }
}

export default new UploadFilesService();
