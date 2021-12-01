"""A Microsub client for the Understory framework."""

import websub
from microsub import server
from understory import web
from understory.web import tx

app = web.application(
    __name__,
    prefix="people",
    args={"nickname": r"[A-Za-z0-9-]+"},
    model=server.model.schemas,
)


@app.wrap
def connect_model(handler, main_app):
    """Connect the model to this transaction's database."""
    tx.sub = server.model(tx.db)
    yield


@app.wrap
def linkify_head(handler, app):
    """Ensure server link is in head of root document."""
    yield
    if tx.request.uri.path == "":
        web.add_rel_links(microsub="/people")


@app.control(r"")
class MicrosubEndpoint:
    """A Microsub endpoint."""

    def get(self):
        """Perform an action or return an activity summary."""
        try:
            form = web.form("action", channel="default")
        except web.BadRequest:
            return app.view.activity(tx.sub.get_following(), tx.sub.get_channels())
        response = {}
        if form.action == "channels":
            response = {"channels": tx.sub.get_channels()}
        if form.action == "follow":
            response = {"items": tx.sub.get_following()}
        elif form.action == "timeline":
            response = {"items": []}
        web.header("Content-Type", "application/json")
        return response

    def post(self):
        """Perform an action."""
        form = web.form("action", channel="default")
        response = {}
        if form.action == "channels":
            tx.sub.add_channel(form.name)
            response = {"channels": tx.sub.get_channels()}
        elif form.action == "search":
            response = {"results": tx.sub.search(form.query)}
        elif form.action == "preview":
            response = tx.sub.preview(form.url)
        elif form.action == "follow":
            tx.sub.follow(form.url)
            response = {"items": tx.sub.get_following()}
            web.enqueue(websub.subscribe, f"{tx.origin}/subscriptions/sent", form.url)
        elif form.action == "unfollow":
            pass
        elif form.action == "timeline":
            pass
        elif form.action == "mute":
            pass
        elif form.action == "unmute":
            pass
        elif form.action == "block":
            pass
        elif form.action == "unblock":
            pass
        web.header("Content-Type", "application/json")
        return response


@app.control(r"search")
class Search:
    """."""

    def get(self):
        """Return search results for given `q`."""
        form = web.form("q")
        return app.view.search(form.q, tx.sub.search(form.q))


@app.control(r"preview")
class Preview:
    """."""

    def get(self):
        """Return a preview of given `url`."""
        form = web.form("url")
        return app.view.preview(
            form.url, tx.sub.preview(form.url), tx.sub.get_channels()
        )


# XXX iPhone-compatible CardDAV support below XXX


@app.control(r"cards")
class Cards:
    """
    All cards on file.

    `OPTIONS`, `PROPFIND` and `REPORT` methods provide CardDAV support.

    """

    def get(self):
        """"""
        return app.view.cards(tx.pub.get_cards(), app.view.render_dict)

    def options(self):
        """Signal capabilities to CardDAV client."""
        web.header("DAV", "1, 2, 3, access-control, addressbook")
        web.header(
            "Allow",
            "OPTIONS, GET, HEAD, POST, PUT, DELETE, TRACE, "
            "COPY, MOVE, MKCOL, PROPFIND, PROPPATCH, LOCK, "
            "UNLOCK, REPORT, ACL",
        )
        tx.response.naked = True
        return ""

    def propfind(self):
        """
        Return a status listing of addressbook/contacts.

        This resource is requsted twice with `Depth` headers of 0 and 1.
        0 is a request for the addressbook itself. 1 is a request for the
        addressbook itself and all contacts in the addressbook. Thus both
        the addressbook itself and each user have an etag.

        """
        # TODO refactor..
        web.header("DAV", "1, 2, 3, access-control, addressbook")

        depth = int(tx.request.headers["Depth"])
        etags = {"": tx.kv["carddav-lasttouch"]}
        if depth == 1:
            for identity in get_resources("identities"):
                etags[identity["-uuid"]] = identity.get(
                    "updated", identity["published"]
                ).timestamp()

        props = list(tx.request.body.iterchildren())[0]
        namespaces = set()
        responses = []

        for uuid, etag in etags.items():
            ok = []
            notfound = []
            for prop in props.iterchildren():
                # supported
                if prop.tag == "{DAV:}current-user-privilege-set":
                    ok.append(
                        """<current-user-privilege-set>
                                     <privilege>
                                         <all />
                                         <read />
                                         <write />
                                         <write-properties />
                                         <write-content />
                                     </privilege>
                                 </current-user-privilege-set>"""
                    )
                if prop.tag == "{DAV:}displayname":
                    ok.append("<displayname>carddav</displayname>")
                if prop.tag == "{DAV:}getetag":
                    ok.append(f'<getetag>"{etag}"</getetag>')
                if prop.tag == "{DAV:}owner":
                    ok.append("<owner>/</owner>")
                if prop.tag == "{DAV:}principal-URL":
                    ok.append(
                        """<principal-URL>
                                     <href>/identities</href>
                                 </principal-URL>"""
                    )
                if prop.tag == "{DAV:}principal-collection-set":
                    ok.append(
                        """<principal-collection-set>
                                     <href>/identities</href>
                                 </principal-collection-set>"""
                    )
                if prop.tag == "{DAV:}current-user-principal":
                    ok.append(
                        """<current-user-principal>
                                     <href>/identities</href>
                                 </current-user-principal>"""
                    )
                if prop.tag == "{DAV:}resourcetype":
                    namespaces.add("CR")
                    if uuid:
                        ok.append("<resourcetype />")
                    else:
                        ok.append(
                            """<resourcetype>
                                         <CR:addressbook />
                                         <collection />
                                     </resourcetype>"""
                        )
                if prop.tag == "{DAV:}supported-report-set":
                    ok.append(
                        """<supported-report-set>
                                     <supported-report>
                                         <report>principal-property-search</report>
                                     </supported-report>
                                     <supported-report>
                                         <report>sync-collection</report>
                                     </supported-report>
                                     <supported-report>
                                         <report>expand-property</report>
                                     </supported-report>
                                     <supported-report>
                                         <report>principal-search-property-set</report>
                                     </supported-report>
                                 </supported-report-set>"""
                    )
                if (
                    prop.tag == "{urn:ietf:params:xml:ns:carddav}"
                    "addressbook-home-set"
                ):
                    namespaces.add("CR")
                    ok.append(
                        """<CR:addressbook-home-set>
                                     <href>/identities</href>
                                 </CR:addressbook-home-set>"""
                    )
                if prop.tag == "{http://calendarserver.org/ns/}" "getctag":
                    namespaces.add("CS")
                    ok.append(f'<CS:getctag>"{etag}"</CS:getctag>')

                # conditionally supported
                if prop.tag == "{http://calendarserver.org/ns/}me-card":
                    namespaces.add("CS")
                    if uuid:
                        notfound.append("<CS:me-card />")
                    else:
                        ok.append(
                            f"""<CS:me-card>
                                      <href>/identities/{tx.owner["-uuid"]}.vcf</href>
                                      </CS:me-card>"""
                        )

                # not supported
                if prop.tag == "{DAV:}add-member":
                    notfound.append("<add-member />")
                if prop.tag == "{DAV:}quota-available-bytes":
                    notfound.append("<quota-available-bytes />")
                if prop.tag == "{DAV:}quota-used-bytes":
                    notfound.append("<quota-used-bytes />")
                if prop.tag == "{DAV:}resource-id":
                    notfound.append("<resource-id />")
                if prop.tag == "{DAV:}sync-token":
                    notfound.append("<sync-token />")
                if prop.tag == "{urn:ietf:params:xml:ns:carddav}" "directory-gateway":
                    namespaces.add("CR")
                    notfound.append("<CR:directory-gateway />")
                if prop.tag == "{urn:ietf:params:xml:ns:carddav}" "max-image-size":
                    namespaces.add("CR")
                    notfound.append("<CR:max-image-size />")
                if prop.tag == "{urn:ietf:params:xml:ns:carddav}" "max-resource-size":
                    namespaces.add("CR")
                    notfound.append("<CR:max-resource-size />")
                if prop.tag == "{http://calendarserver.org/ns/}" "email-address-set":
                    namespaces.add("CS")
                    notfound.append("<CS:email-address-set />")
                if prop.tag == "{http://calendarserver.org/ns/}" "push-transports":
                    namespaces.add("CS")
                    notfound.append("<CS:push-transports />")
                if prop.tag == "{http://calendarserver.org/ns/}" "pushkey":
                    namespaces.add("CS")
                    notfound.append("<CS:pushkey />")
                if prop.tag == "{http://me.com/_namespace/}" "bulk-requests":
                    namespaces.add("ME")
                    notfound.append("<ME:bulk-requests />")
            href = "/identities"
            if uuid:
                href += f"/{uuid}.vcf"
            responses.append((href, ok, notfound))
        tx.response.naked = True
        raise web.MultiStatus(view.carddav(namespaces, responses))

    def report(self):
        """Return a full listing for each requested identity."""
        etags = {}
        for identity in get_resources("identities"):
            etags[identity["-uuid"]] = identity.get(
                "updated", identity["published"]
            ).timestamp()
        children = list(tx.request.body.iterchildren())
        # XXX props = children[0]  # TODO soft-code prop responses
        responses = []
        for href in children[1:]:
            uuid = href.text.rpartition("/")[2].partition(".")[0]
            ok = [
                f'<getetag>"{etags[uuid]}"</getetag>',
                f"<CR:address-data>{generate_vcard(uuid)}</CR:address-data>",
            ]
            notfound = []
            responses.append((href.text, ok, notfound))
        tx.response.naked = True
        raise web.MultiStatus(view.carddav(set(["CR"]), responses))


@app.control(r"cards/{nickname}")
class Card:
    """A single card on file."""

    def get(self):
        """"""
        # try:
        #     resource = tx.db.select("cache", where="url = ?",
        #                             vals=[f"https://{self.resource}"])[0]
        # except IndexError:
        #     resource = tx.db.select("cache", where="url = ?",
        #                             vals=[f"http://{self.resource}"])[0]
        return app.view.card(tx.pub.get_card(self.nickname))


@app.control(r"cards/{nickname}.vcf")
class VCard:
    """
    A single card on file, represented as a vCard.

    `PUT` and `DELETE` methods provide CardDAV support.

    """

    def get(self):
        """"""
        web.header("Content-Type", "text/vcard")
        return generate_vcard(self.nickname)

    def put(self):
        """
        add or update a identity

        """
        # TODO only add if "if-none-match" is found and identity isn't
        try:
            print("if-none-match", tx.request.headers.if_none_match)
        except AttributeError:
            pass
        else:
            try:
                identities.get_identity_by_uuid(self.card_id)
            except ResourceNotFound:
                pass
            else:
                raise web.Conflict("identity already exists")

        # TODO only update if "if-match" matches etag on hand
        try:
            request_etag = str(tx.request.headers.if_match).strip('"')
            print("if-match", request_etag)
        except AttributeError:
            pass
        else:
            identity = identities.get_identity_by_uuid(self.card_id)
            current_etag = identity.get("updated", identity["published"]).timestamp()
            print("current etag", current_etag)
            if request_etag != current_etag:
                raise web.Conflict("previous edit already exists")

        # TODO non-standard type-params (url) not handled by vobject

        card = vobject.readOne(tx.request.body.decode("utf-8"))

        name = card.fn.value.strip()

        extended = {}
        n = card.n.value

        def explode(key):
            item = getattr(n, key)
            if isinstance(item, list):
                extended[key] = ";".join(item)
            else:
                extended[key] = [item]

        explode("prefix")
        explode("given")
        explode("additional")
        explode("family")
        explode("suffix")

        # TODO identity_type = "identity"
        basic = {"name": name, "uuid": self.card_id}

        # TODO organizations = [o.value[0]
        # TODO                  for o in card.contents.get("org", [])]
        # TODO for organization in organizations:
        # TODO     if organization == name:
        # TODO         identity_type = "organization"

        # TODO telephones = []
        # TODO for tel in card.contents.get("tel", []):
        # TODO     telephones.append((tel.value, tel.params["TYPE"]))
        # TODO websites = []
        # TODO for url in card.contents.get("url", []):
        # TODO     type = url.params.get("TYPE", [])
        # TODO     for label in card.contents.get("x-ablabel"):
        # TODO         if label.group == url.group:
        # TODO             type.append(label.value)
        # TODO     print(url.value, type)
        # TODO     print()
        # TODO     websites.append((url.value, type))

        # photo = card.contents.get("photo")[0]
        # print()
        # print(photo)
        # print()
        # print(photo.group)
        # print(photo.params.get("ENCODING"))
        # print(photo.params.get("X-ABCROP-RECTANGLE"))
        # print(photo.params.get("TYPE", []))
        # print(len(photo.value))
        # print()
        # filepath = tempfile.mkstemp()[1]
        # with open(filepath, "wb") as fp:
        #     fp.write(photo.value)
        # photo_id = canopy.branches["images"].photos.upload(filepath)
        # extended["photos"] = [photo_id]

        try:
            details = identities.get_identity_by_uuid(self.card_id)
        except ResourceNotFound:
            print("NEW identity!")
            print(basic)
            print(extended)
            quick_draft("identity", basic, publish="Identity imported from iPhone.")
            # XXX details = create_identity(access="private", uid=self.card_id,
            # XXX                          **basic)
            # XXX details = update_identity(identifier=details["identifier"],
            # XXX                  telephones=telephones, websites=websites,
            # XXX                  **extended)
            print("CREATED")
        else:
            print("EXISTING identity!")
            print(details)
            print("UPDATED")
        # XXX     basic.update(extended)
        # XXX     details = update_identity(identifier=details["identifier"],
        # XXX                      telephones=telephones, websites=websites,
        # XXX                      **basic)
        identity = identities.get_identity_by_uuid(self.card_id)
        etag = identity.get("updated", identity["published"]).timestamp()
        web.header("ETag", f'"{etag}"')
        tx.response.naked = True
        raise web.Created("created identity", f"/identities/{self.card_id}.vcf")

    def delete(self):
        """
        delete a identity

        This method provides CardDAV support.

        """
        # delete_resource(...)
        tx.response.naked = True
        return f"""<?xml version="1.0"?>
                   <multistatus xmlns="DAV:">
                     <response>
                       <href>/identities/{self.card_id}.vcf</href>
                       <status>HTTP/1.1 200 OK</status>
                     </response>
                   </multistatus>"""
