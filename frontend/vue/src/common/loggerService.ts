import {useAuthStore} from "@/stores/auth";
/*
 * Manage Client Side Logging
 **/
export class LoggerService {
  private clientSideLogging = false;
  private loggingRole = "developer";
  public log(element: any) {
    const uRole = useAuthStore().getRole();
    if (this.clientSideLogging === true || (uRole !== null && uRole === this.loggingRole)) {
      console.log(element);
    }
  }
  public error(element: any) {
    const uRole = useAuthStore().getRole();
    if (this.clientSideLogging === true || (uRole !== null && uRole === this.loggingRole)) {
      console.error(element);
    }
  }
}
