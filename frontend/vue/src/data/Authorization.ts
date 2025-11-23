/**
 * A logged in User with a name, preferred language, university, faculty and role
 */
class User {
  id: string;
  username: string;
  mail: string;
  firstName: string;
  lastName: string;
  preferedLanguage: string;
  university: string;
  faculty: string;
  role: string;

  constructor(
    id: string,
    username: string,
    mail: string,
    firstName: string,
    lastName: string,
    preferedLanguage: string,
    university: string,
    faculty: string,
    role: string,
  ) {
    this.id = id;
    this.username = username;
    this.mail = mail;
    this.firstName = firstName;
    this.lastName = lastName;
    this.preferedLanguage = preferedLanguage;
    this.university = university;
    this.faculty = faculty;
    this.role = role;
  }
}

class JWTAccess {
  token: string | null;
  key: string;
  expiration: string | null;
  refreshToken: string | null;
  refreshKey: string;
  refreshExpiration: string | null;

  /**
   * Constructs a JWT access token
   *
   * @param {string | null} token - JWT access_token
   * @param {string} key - JWT access_token local storage key
   * @param {string | null} expiration - JWT access_token expiration
   * @param {string | null} refreshToken - JWT refresh_token
   * @param {string} refreshKey - JWT refresh_token local storage key
   * @param {string | null} refreshExpiration - JWT refresh_token expiration
   */
  constructor(
    token: string | null = null,
    key: string = "hans_access_token",
    expiration: string | null = null,
    refreshToken: string | null = null,
    refreshKey: string = "hans_refresh_token",
    refreshExpiration: string | null = null,
  ) {
    this.token = token;
    this.key = key;
    this.expiration = expiration;
    this.refreshToken = refreshToken;
    this.refreshKey = refreshKey;
    this.refreshExpiration = refreshExpiration;
  }
}

export {User, JWTAccess};
