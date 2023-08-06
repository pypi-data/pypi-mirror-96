package com.anaconda.skein;

import com.google.common.base.Joiner;

import org.apache.hadoop.fs.FileStatus;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.yarn.api.records.ApplicationId;
import org.apache.hadoop.yarn.api.records.LocalResource;
import org.apache.hadoop.yarn.api.records.LocalResourceType;
import org.apache.hadoop.yarn.api.records.LocalResourceVisibility;
import org.apache.hadoop.yarn.api.records.URL;
import org.apache.hadoop.yarn.util.ConverterUtils;

import java.io.IOException;
import java.io.OutputStream;
import java.net.InetAddress;
import java.net.URI;
import java.net.URISyntaxException;
import java.net.UnknownHostException;
import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.Set;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.ThreadFactory;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.TimeUnit;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class Utils {
  // An exception indicating an unsupported Hadoop feature was requested
  public static class UnsupportedFeatureException extends IllegalArgumentException {
    public UnsupportedFeatureException(String msg) {
      super(msg);
    }
  }

  public static String getSkeinVersion() {
    return Utils.class.getPackage().getImplementationVersion();
  }

  public static <T> T popfirst(Set<T> s) {
    for (T out: s) {
      s.remove(out);
      return out;
    }
    return null;
  }

  private static final char[] HEX = "0123456789ABCDEF".toCharArray();

  public static String hexEncode(byte[] bytes) {
    char[] out = new char[bytes.length * 2];
    for (int j = 0; j < bytes.length; j++) {
      int v = bytes[j] & 0xFF;
      out[j * 2] = HEX[v >>> 4];
      out[j * 2 + 1] = HEX[v & 0x0F];
    }
    return new String(out);
  }

  private static final String MEM_REGEX = "[0-9.]+ [KMG]B";
  public static final Pattern EXCEEDED_PMEM_PATTERN =
      Pattern.compile(MEM_REGEX + " of " + MEM_REGEX + " physical memory used");
  public static final Pattern EXCEEDED_VMEM_PATTERN =
      Pattern.compile(MEM_REGEX + " of " + MEM_REGEX + " virtual memory used");

  public static String formatExceededMemMessage(String diagnostics, Pattern pattern) {
    Matcher matcher = pattern.matcher(diagnostics);
    return (matcher.find() ? matcher.group() :
            "Container killed by YARN for exceeding memory limits");
  }

  public static String formatMemory(double mem) {
    if (mem < 1024) {
      return String.format("%.1f MiB", mem);
    } else if (mem < 1024 * 1024) {
      return String.format("%.1f GiB", mem / 1024);
    } else {
      return String.format("%.1f TiB", mem / (1024 * 1024));
    }
  }

  public static String formatRuntime(long delta) {
    long secs = delta / 1000;
    long hours = secs / (60 * 60);
    secs = secs % (60 * 60);
    long mins = secs / 60;
    secs = secs % 60;

    if (hours > 0) {
      return String.format("%dh %dm", hours, mins);
    }
    else if (mins > 0) {
      return String.format("%dm %ds", mins, secs);
    } else {
      return String.format("%ds", secs);
    }
  }

  public static final class CustomThreadFactory implements ThreadFactory {
    private String baseName;
    private boolean isDaemon;
    private int count = 0;

    public CustomThreadFactory(String baseName, boolean isDaemon) {
      this.baseName = baseName;
      this.isDaemon = isDaemon;
    }

    public Thread newThread(Runnable r) {
      String name = baseName + "-" + count;
      count += 1;
      Thread out = new Thread(r, name);
      out.setDaemon(isDaemon);
      return out;
    }
  }

  public static ThreadPoolExecutor newThreadPoolExecutor(String name,
      int minCount, int maxCount, boolean isDaemon) {
    return new ThreadPoolExecutor(
        minCount, maxCount, 60, TimeUnit.SECONDS,
        new LinkedBlockingQueue<Runnable>(),
        new CustomThreadFactory(name, isDaemon));
  }

  public static void configureNettyNativeWorkDir() {
    final String property = "io.netty.native.workdir";

    // Already set by user, do nothing
    if (System.getProperty(property) != null) {
      return;
    }

    // Set to current directory if we're in a container
    if (System.getenv("CONTAINER_ID") != null) {
      System.setProperty(property, "./");
    }
  }

  public static String formatAcl(List<String> users, List<String> groups) {
    // "*" in either groups or users -> "*"
    if (users.contains("*") || groups.contains("*")) {
      return "*";
    }

    StringBuilder builder = new StringBuilder();
    Joiner joiner = Joiner.on(",");

    if (users != null) {
      joiner.appendTo(builder, users);
    }

    builder.append(" ");

    if (groups != null) {
      joiner.appendTo(builder, groups);
    }

    return builder.toString();
  }

  public static ApplicationId appIdFromString(String appId) {
    // Parse applicationId_{timestamp}_{id}
    String[] parts = appId.split("_");
    if (parts.length < 3) {
      return null;
    }
    long timestamp = Long.valueOf(parts[1]);
    int id = Integer.valueOf(parts[2]);
    return ApplicationId.newInstance(timestamp, id);
  }

  public static void stringToFile(String data, OutputStream out)
      throws IOException {
    try {
      out.write(data.getBytes(StandardCharsets.UTF_8));
    } finally {
      out.close();
    }
  }

  public static LocalResource localResource(FileSystem fs, Path path,
        LocalResourceType type) throws IOException {
    FileStatus status = fs.getFileStatus(path);
    return LocalResource.newInstance(ConverterUtils.getYarnUrlFromPath(path),
                                     type,
                                     LocalResourceVisibility.APPLICATION,
                                     status.getLen(),
                                     status.getModificationTime());
  }

  public static Path pathFromUrl(URL url) {
    try {
      return ConverterUtils.getPathFromYarnURL(url);
    } catch (URISyntaxException exc) {
      throw new IllegalArgumentException(exc.getMessage());
    }
  }

  /** Compare two filesystems for equality.
   *
   * Borrowed (with some modification) from Apache Spark. License header:
   * --------------------------------------------------------------------
   *
   * Licensed to the Apache Software Foundation (ASF) under one or more
   * contributor license agreements.  See the NOTICE file distributed with
   * this work for additional information regarding copyright ownership.
   * The ASF licenses this file to You under the Apache License, Version 2.0
   * (the "License"); you may not use this file except in compliance with
   * the License.  You may obtain a copy of the License at
   *
   *    http://www.apache.org/licenses/LICENSE-2.0
   *
   * Unless required by applicable law or agreed to in writing, software
   * distributed under the License is distributed on an "AS IS" BASIS,
   * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   * See the License for the specific language governing permissions and
   * limitations under the License.
   **/
  public static boolean equalFs(FileSystem srcFs, FileSystem dstFs) {
    String srcScheme = srcFs.getScheme();
    String dstScheme = dstFs.getScheme();

    if (srcScheme == null || dstScheme == null || !srcScheme.equals(dstScheme)) {
      return false;
    }

    URI srcUri = srcFs.getUri();
    URI dstUri = dstFs.getUri();

    String srcAuth = srcUri.getAuthority();
    String dstAuth = dstUri.getAuthority();
    if (srcAuth != null && dstAuth != null && !srcAuth.equalsIgnoreCase(dstAuth)) {
      return false;
    }

    String srcHost = srcUri.getHost();
    String dstHost = dstUri.getHost();

    if (srcHost != null && dstHost != null && !srcHost.equals(dstHost)) {
      try {
        srcHost = InetAddress.getByName(srcHost).getCanonicalHostName();
        dstHost = InetAddress.getByName(dstHost).getCanonicalHostName();
      } catch (UnknownHostException exc) {
        return false;
      }
    }

    return srcHost.equals(dstHost) && srcUri.getPort() == dstUri.getPort();
  }
}
